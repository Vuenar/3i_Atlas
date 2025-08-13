"""
3I/ATLAS proximity calculator (single-file) - versão com design melhorado + Mkm + gráfico ajustado
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from astropy.time import Time
from astroquery.jplhorizons import Horizons
import math
from PIL import Image, ImageTk

# Importações do Matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

# Conversion constant
AU_TO_KM = 149597870.7

# Planet mapping: NAIF/HORIZONS major-body barycenter IDs (1..8)
PLANET_CODES = {
    'Mercury': 1,
    'Venus': 2,
    'Earth (EMB)': 3,
    'Mars': 4,
    'Jupiter': 5,
    'Saturn': 6,
    'Uranus': 7,
    'Neptune': 8,
    'Sun': 10, # Adicionando o Sol
}


class ProximityApp:
    def __init__(self, master):
        self.master = master
        master.title('3I/ATLAS proximity (C/2025 N1) - Brasília time')
        master.resizable(False, False)

        # Tema moderno
        style = ttk.Style(master)
        style.theme_use("clam")

        # Fontes e estilos
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TEntry", padding=4)
        
        # Frame principal
        frm = ttk.Frame(master, padding=15)
        frm.grid(row=0, column=0, sticky='nsew')

        # ====== Carregar a logo antes do título ======
        logo_img = Image.open("assets/img/logo.png")
        logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
        self.logo_tk = ImageTk.PhotoImage(logo_img)

        master.iconphoto(False, self.logo_tk)

        title_label = ttk.Label(
            frm,
            text=" 3I/ATLAS - Calculadora de Proximidade",
            image=self.logo_tk,
            compound="left",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Date inputs
        ttk.Label(frm, text='Dia').grid(row=1, column=0)
        self.day_var = tk.StringVar(value=str(datetime.now(ZoneInfo('America/Sao_Paulo')).day))
        self.day = ttk.Entry(frm, width=5, textvariable=self.day_var)
        self.day.grid(row=2, column=0, padx=5, pady=3)

        ttk.Label(frm, text='Mês').grid(row=1, column=1)
        self.month_var = tk.StringVar(value=str(datetime.now(ZoneInfo('America/Sao_Paulo')).month))
        self.month = ttk.Entry(frm, width=5, textvariable=self.month_var)
        self.month.grid(row=2, column=1, padx=5, pady=3)

        ttk.Label(frm, text='Ano').grid(row=1, column=2)
        self.year_var = tk.StringVar(value=str(datetime.now(ZoneInfo('America/Sao_Paulo')).year))
        self.year = ttk.Entry(frm, width=8, textvariable=self.year_var)
        self.year.grid(row=2, column=2, padx=5, pady=3)

        # Time inputs
        ttk.Label(frm, text='Hora (0-23)').grid(row=3, column=0)
        self.hour_var = tk.StringVar(value=str(datetime.now(ZoneInfo('America/Sao_Paulo')).hour))
        self.hour = ttk.Entry(frm, width=5, textvariable=self.hour_var)
        self.hour.grid(row=4, column=0, padx=5, pady=3)

        ttk.Label(frm, text='Minuto').grid(row=3, column=1)
        self.minute_var = tk.StringVar(value=str(datetime.now(ZoneInfo('America/Sao_Paulo')).minute))
        self.minute = ttk.Entry(frm, width=5, textvariable=self.minute_var)
        self.minute.grid(row=4, column=1, padx=5, pady=3)

        ttk.Label(frm, text='Segundo').grid(row=3, column=2)
        self.second_var = tk.StringVar(value='0')
        self.second = ttk.Entry(frm, width=8, textvariable=self.second_var)
        self.second.grid(row=4, column=2, padx=5, pady=3)

        ttk.Label(frm, text='Timezone: America/Sao_Paulo (Brasília)', 
                  font=("Segoe UI", 9, "italic")).grid(row=5, column=0, columnspan=3, pady=(10,5))

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(8,0))

        self.calc_btn = ttk.Button(btn_frame, text='Calcular proximidade', command=self.calculate)
        self.calc_btn.grid(row=0, column=0, padx=8)

        self.reset_btn = ttk.Button(btn_frame, text='Resetar', command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=8)

        # Results area
        self.results = tk.Text(frm, width=72, height=14, wrap='word',
                               bg="#f9f9f9", fg="#333333", font=("Consolas", 10))
        self.results.grid(row=7, column=0, columnspan=3, pady=(12,0))
        self.results.insert('1.0', 'Resultados aparecerão aqui. Clique em "Calcular proximidade" para iniciar.\n')
        self.results.configure(state='disabled')

        self.chart_widget = None

    def _set_results(self, text):
        self.results.configure(state='normal')
        self.results.delete('1.0', tk.END)
        self.results.insert('1.0', text)
        self.results.configure(state='disabled')

    def reset(self):
        now = datetime.now(ZoneInfo('America/Sao_Paulo'))
        self.day_var.set(str(now.day))
        self.month_var.set(str(now.month))
        self.year_var.set(str(now.year))
        self.hour_var.set(str(now.hour))
        self.minute_var.set(str(now.minute))
        self.second_var.set('0')
        self._set_results('Campos resetados. Insira nova data/hora e clique em "Calcular proximidade".')

        if self.chart_widget:
            self.chart_widget.get_tk_widget().destroy()
            self.chart_widget = None

    def calculate(self):
        self.calc_btn.config(state='disabled')
        try:
            d = int(self.day_var.get())
            m = int(self.month_var.get())
            y = int(self.year_var.get())
            hh = int(self.hour_var.get())
            mm = int(self.minute_var.get())
            ss = int(self.second_var.get() or 0)

            tz = ZoneInfo('America/Sao_Paulo')
            dt_local = datetime(y, m, d, hh, mm, ss, tzinfo=tz)
            dt_utc = dt_local.astimezone(timezone.utc)

            t = Time(dt_utc, scale='utc')
            jd_tdb = t.tdb.jd

            self._set_results('Consultando JPL HORIZONS para a data (TDB JD = {:.6f})...\n'.format(jd_tdb))

            comet = Horizons(id='C/2025 N1', id_type='designation', location='@0', epochs=jd_tdb)
            comet_vec = comet.vectors()
            cx, cy, cz = float(comet_vec['x'][0]), float(comet_vec['y'][0]), float(comet_vec['z'][0])

            distances = []
            for pname, pid in PLANET_CODES.items():
                p = Horizons(id=str(pid), id_type='majorbody', location='@0', epochs=jd_tdb)
                pvec = p.vectors()
                px, py, pz = float(pvec['x'][0]), float(pvec['y'][0]), float(pvec['z'][0])
                dist_au = math.sqrt((cx-px)**2 + (cy-py)**2 + (cz-pz)**2)
                distances.append((pname, dist_au))

            distances.sort(key=lambda x: x[1])

            nearest_name, nearest_au = distances[0]
            nearest_km = nearest_au * AU_TO_KM
            nearest_mkm = nearest_km / 1_000_000

            out_lines = [
                f'Data e hora (Brasília): {dt_local.strftime("%Y-%m-%d %H:%M:%S %Z")})',
                '\nResultado:',
                f'Objeto consultado: 3I/ATLAS (C/2025 N1)',
                f'Planeta mais próximo nesse instante: {nearest_name}',
                'Distância: {:.6f} AU  (≈ {:.0f} km ≈ {:.2f} Mkm)'.format(nearest_au, nearest_km, nearest_mkm),
                '\nTabela de distâncias (AU):'
            ]
            for pname, dau in distances:
                km = dau * AU_TO_KM
                mkm = km / 1_000_000
                out_lines.append('  - {:12s} : {:.6f} AU (≈ {:.0f} km ≈ {:.2f} Mkm)'.format(pname, dau, km, mkm))

            self._set_results('\n'.join(out_lines))

            # ===== Gráfico =====
            planet_names = [p[0] for p in distances]
            distances_mkm = [(p[1] * AU_TO_KM) / 1_000_000 for p in distances]

            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)

            colors = plt.cm.tab10(np.linspace(0, 1, len(planet_names)))
            bars = ax.bar(planet_names, distances_mkm, color=colors, edgecolor='black')

            for bar, value in zip(bars, distances_mkm):
                ax.text(bar.get_x() + bar.get_width()/4, bar.get_height(),
                        f"{value:.2f}", ha='center', va='bottom', fontsize=8)

            ax.set_ylabel("Distância (Milhões de km)")
            ax.set_xlabel("Planetas")
            ax.set_title("Distância do 3I/ATLAS para cada planeta")
            ax.tick_params(axis='x', rotation=45)
            ax.set_xticklabels(planet_names, ha='right')

            fig.tight_layout(pad=2.0)

            if self.chart_widget:
                self.chart_widget.get_tk_widget().destroy()

            self.chart_widget = FigureCanvasTkAgg(fig, master=self.master)
            self.chart_widget.draw()
            self.chart_widget.get_tk_widget().grid(row=8, column=0, columnspan=3, pady=10)

        except Exception as e:
            messagebox.showerror('Erro', f'Ocorreu um erro:\n{e}')
            self._set_results('Erro ao executar a consulta. Verifique a conexão com a internet e os valores inseridos.')
        finally:
            self.calc_btn.config(state='normal')


if __name__ == '__main__':
    root = tk.Tk()
    app = ProximityApp(root)
    root.mainloop()
