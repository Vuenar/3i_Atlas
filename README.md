# 3i Atlas Tool 📊🐍

[![Status](https://img.shields.io/badge/status-finalizado-brightgreen?style=for-the-badge)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)]()
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)]()

## 📌 Sobre o Projeto

O **3i Atlas Tool** é um projeto desenvolvido durante a disciplina **Tópicos de Big Data em Python**, no curso Tecnólogo em Análise e Desenvolvimento de Sistemas da **Estácio**.  
Essa disciplina é **extensionista**, promovendo a aplicação prática de conceitos de Big Data para resolver problemas reais.

O objetivo do projeto é **processar, analisar e visualizar dados de forma eficiente** utilizando a linguagem Python, com foco em **tratamento, manipulação e análise de grandes volumes de dados**.

---

## 🎯 Objetivos

- Aplicar conceitos aprendidos em sala de aula de forma prática.
- Demonstrar o uso de bibliotecas e ferramentas do ecossistema Python para Big Data.
- Criar uma base de código modular e escalável.
- Produzir visualizações e relatórios que auxiliem na interpretação de dados.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.10+** 🐍  
- **Pandas** – Manipulação e tratamento de dados.
- **NumPy** – Operações numéricas e vetoriais.
- **Matplotlib / Seaborn** – Visualização gráfica.
- **Jupyter Notebook** – Ambiente interativo de desenvolvimento.
- **Git & GitHub** – Controle de versão e colaboração.

---

## 📂 Estrutura do Projeto

```
3i-Atlas-Tool/
│── data/               # Conjunto de dados utilizados
│── notebooks/          # Análises e protótipos
│── src/                # Código-fonte principal
│── requirements.txt    # Dependências do projeto
│── README.md           # Documentação do projeto
```

---

## 🔍 Metodologia Utilizada

O desenvolvimento seguiu a abordagem **Data Pipeline**, composta pelas etapas:

1. **Coleta de Dados** – Importação e carregamento dos datasets.
2. **Tratamento de Dados** – Limpeza, padronização e formatação.
3. **Análise Exploratória (EDA)** – Estatísticas descritivas e identificação de padrões.
4. **Visualização** – Criação de gráficos para melhor interpretação dos resultados.
5. **Documentação** – Registro do processo e resultados obtidos.

---

## 📦 Instalação e Uso

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/3i-Atlas-Tool.git
```

2. **Acesse o diretório**
```bash
cd 3i-Atlas-Tool
```

3. **Crie um ambiente virtual (opcional, mas recomendado)**
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Execute os notebooks ou scripts**
```bash
jupyter notebook
```

---

## 📊 Exemplo de Uso

Exemplo de carregamento e visualização de dados:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/exemplo.csv")
print(df.head())

df['coluna'].value_counts().plot(kind='bar')
plt.show()
```

---

## 📜 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

## 👨‍💻 Autor

Desenvolvido por **Uelison Couto** 💻  
Curso: Tecnólogo em Análise e Desenvolvimento de Sistemas – **Estácio**  
Disciplina: Tópicos de Big Data em Python – Extensão Acadêmica


