import streamlit as st
import pandas as pd
import json
from collections import defaultdict

# Carrega o arquivo e exibe na interface
st.title("Conversor de Horários para JSON")
uploaded_file = st.file_uploader("Escolha o arquivo Excel", type="xlsx")

if uploaded_file:
    # Lê o Excel
    df = pd.read_excel(uploaded_file, sheet_name="Dados")
    df['Curso'] = df['Curso'].ffill()  # Preenche valores de curso
    df['Horário'] = df['Horário'].ffill()
    df['Período'] = df['Período'].ffill()
    st.write(df)
    
    # Obter o nome do curso
    curso_nome = df['Curso'].iloc[0]  # Pega o primeiro valor da coluna 'Curso' (assumindo que é o mesmo para todas as linhas)

    # Inicializar estrutura de saída com o nome do curso
    output = {
        "curso": curso_nome,
        "periodos": {}
    }

    # Iterar sobre cada período, horário e dia da semana
    for period, period_df in df.groupby("Período"):
        period_list = []
        for horario, horario_df in period_df.groupby("Horário"):
            for day in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]:
                day_data = horario_df[day].dropna()
                if not day_data.empty:
                    item = {
                        "horario": horario,
                        "dia": day,
                    }
                    # Preencher item com as informações de cada coluna
                    for _, row in horario_df.iterrows():
                        info_key = row["Informação"].lower()
                        item[info_key] = row[day]

                    period_list.append(item)

        # Adicionar o período ao output apenas se houver dados
        if period_list:
            output["periodos"][period] = period_list

    # Exibir JSON formatado
    st.write(json.dumps(output, indent=4, ensure_ascii=False))