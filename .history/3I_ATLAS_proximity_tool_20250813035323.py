"""
3I/ATLAS proximity calculator (single-file) - versão com gráfico maior e interface de cor única
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from astropy.time import Time
from astroquery.jplhorizons import Horizons
import math
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

AU_TO_KM = 149597870.7

PLANET_CODES = {
    'Mercury': 1,
    'Venus': 2,
    'Earth (EMB)': 3,
    'Mars': 4,
    'Jupiter': 5,
    'Saturn': 6,
    'Uranus': 7,
    'Neptune': 8,
    'Sun': 10,
}

class ProximityApp:
    def __init__(self, master):
        self.master = master
        master.title('3I/ATLAS proximity (C/2025 N1) - Brasília time')
        master.resizable(False, False)

        # Cor única
        self.bg_color = "#2E2E3A"
        master.configure(bg=self.bg_color)

        style = ttk.Style(master)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10), background=self.bg_color, foreground="white")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TEntry", padding=4)

        # Frame principal
        frm = ttk.Frame(master, padding=15)
        frm.grid(row=0, column=0, sticky='nsew')
        frm.configure(style="TFrame")

        # Logo
        logo_img = Image.open("assets/img/logo.png")
        logo_img = logo_img.resize((32, 32), Image.Resampling.LANCZOS)
        self.logo_tk = ImageTk.PhotoImage(logo_img)
        master.iconphoto(False, self.logo_tk)

        title_label = ttk.Label(
            frm,
            text=" 3I/ATLAS - Calculadora de Proximidade",
            image=self.logo_tk,
            compound="left",
            font=("Segoe UI", 14, "bold"),
            background=self.bg_color,
            foreground="white"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Inputs
        self.add_label_entry(frm, "Dia", 1, 0, str(datetime.now(ZoneInfo('America/Sao_Paulo')).day), 5)
        self.add_label_entry(frm, "Mês", 1, 1, str(datetime.now(ZoneInfo('America/Sao_Paulo')).month), 5)
        self.add_label_entry(frm, "Ano", 1, 2, str(datetime.now(ZoneInfo('America/Sao_Paulo')).year), 8)
        self.add_label_entry(frm, "Hora (0-23)", 3, 0, str(datetime.now(ZoneInfo('America/Sao_Paulo')).hour), 5)
        self.add_label_entry(frm, "Minuto", 3, 1, str(datetime.now(ZoneInfo('America/Sao_Paulo')).minute), 5)
        self.add_label_entry(frm, "Segundo", 3, 2, "0", 8)

        ttk.Label(frm, text='Timezone: America/Sao_Paulo (Brasília)', 
                  font=("Segoe UI", 9, "italic"),
                  background=self.bg_color,
                  foreground="white").grid(row=5, column=0, columnspan=3, pady=(10,5))

        # Botões
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(8,0))
        self.calc_btn = ttk.Button(btn_frame, text='Calcular proximidade', command=self.calculate)
        self.calc_btn.grid(row=0, column=0, padx=8)
        self.reset_btn = ttk.Button(btn_frame, text='Resetar', command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=8)

        # Resultados
        self.results = tk.Text(frm, width=72, height=14, wrap='word',
                               bg=self.bg_color, fg="white", font=("Consolas", 10))
        self.results.grid(row=7, column=0, columnspan=3, pady=(12,0))
        self.results.insert('1.0', 'Resultados aparecerão aqui.\n')
        self.results.configure(state='disabled')

        self.chart_widget = None

    def add_label_entry(self, frame, text, row, col, default, width):
        var = tk.StringVar(value=default)
        ttk.Label(frame, text=text, background=self.bg_color, foreground="white").grid(row=row, column=col)
        entry = ttk.Entry(frame, width=width, textvariable=var)
        entry.grid(row=row+1, column=col, padx=5, pady=3)
        setattr(self, f"{text.split()[0].lower()}_var", var)
        setattr(self, text.split()[0].lower(), entry)

    def _set_results(self, text):
        self.results.configure(state='normal')
        self.results.delete('1.0', tk.END)
        self.results.insert('1.0', text)
        self.results.configure(state='disabled')

    def reset(self):
        now = datetime.now(ZoneInfo('America/Sao_Paulo'))
        self.dia_var.set(str(now.day))
        self.mês_var.set(str(now.month))
        self.ano_var.set(str(now.year))
        self.hora_var.set(str(now.hour))
        self.minuto_var.set(str(now.minute))
        self.segundo_var.set('0')
        self._set_results('Campos resetados.\n')
        if self.chart_widget:
            self.chart_widget.get_tk_widget().destroy()
            self.chart_widget = None

    def calculate(self):
        self.calc_btn.config(state='disabled')
        try:
            d = int(self.dia_var.get())
            m = int(self.mês_var.get())
            y = int(self.ano_var.get())
            hh = int(self.hora_var.get())
            mm = int(self.minuto_var.get())
            ss = int(self.segundo_var.get() or 0)

            tz = ZoneInfo('America/Sao_Paulo')
            dt_local = datetime(y, m, d, hh, mm, ss, tzinfo=tz)
            dt_utc = dt_local.astimezone(timezone.utc)

            t = Time(dt_utc, scale='utc')
            jd_tdb = t.tdb.jd

            comet = Horizons(id='C/2025 N1', id_type='designation', location='@0', epochs=jd_tdb)
            comet_vec = comet.vectors()
            cx, cy, cz = map(float, (comet_vec['x'][0], comet_vec['y'][0], comet_vec['z'][0]))

            distances = []
            for pname, pid in PLANET_CODES.items():
                p = Horizons(id=str(pid), id_type='majorbody', location='@0', epochs=jd_tdb)
                pvec = p.vectors()
                px, py, pz = map(float, (pvec['x'][0], pvec['y'][0], pvec['z'][0]))
                dist_au = math.sqrt((cx-px)**2 + (cy-py)**2 + (cz-pz)**2)
                distances.append((pname, dist_au))

            distances.sort(key=lambda x: x[1])

            nearest_name, nearest_au = distances[0]
            nearest_km = nearest_au * AU_TO_KM
            nearest_mkm = nearest_km / 1_000_000

            out_lines = [f'Data e hora (Brasília): {dt_local.strftime("%Y-%m-%d %H:%M:%S %Z")})',
                         f'Objeto consultado: 3I/ATLAS (C/2025 N1)',
                         f'Planeta mais próximo: {nearest_name}',
                         'Distância: {:.6f} AU  (≈ {:.0f} km ≈ {:.2f} Mkm)'.format(nearest_au, nearest_km, nearest_mkm),
                         '\nTabela de distâncias:']
            for pname, dau in distances:
                km = dau * AU_TO_KM
                mkm = km / 1_000_000
                out_lines.append(f'  - {pname:12s} : {dau:.6f} AU (≈ {km:.0f} km ≈ {mkm:.2f} Mkm)')

            self._set_results('\n'.join(out_lines))

            # Gráfico
            planet_names = [p[0] for p in distances]
            distances_mkm = [(p[1] * AU_TO_KM) / 1_000_000 for p in distances]
            fig = Figure(figsize=(8, 5), dpi=100)
            ax = fig.add_subplot(111)
            colors = plt.cm.tab10(np.linspace(0, 1, len(planet_names)))
            bars = ax.bar(planet_names, distances_mkm, color=colors, edgecolor='black')

            for bar, value in zip(bars, distances_mkm):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f"{value:.2f}", ha='center', va='bottom', fontsize=8, color='black')

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
        finally:
            self.calc_btn.config(state='normal')


if __name__ == '__main__':
    root = tk.Tk()
    app = ProximityApp(root)
    root.mainloop()
