import streamlit as st
import pandas as pd
import io
import json
import os
import pdfkit  # Certifique-se de que o pdfkit está instalado
from openpyxl import Workbook
import tempfile
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def app():

    def fetch_collection_data(db_name, collection_name):
        db = st.session_state.db
        collection = db[collection_name]
        data = list(collection.find())
        for record in data:
            record.pop('_id', None)
        return data

    def carregar_tabelas():
        periodos_df = pd.DataFrame(fetch_collection_data("ipog", "periodos"))
        professores = pd.DataFrame(fetch_collection_data("ipog", "professores"))
        cursos = pd.DataFrame(fetch_collection_data("ipog", "cursos"))
        modalidades = pd.DataFrame(fetch_collection_data("ipog", "modalidades"))

        horarios = fetch_collection_data("ipog", "horarios")[0]['horarios']
        dias = fetch_collection_data("ipog", "dias")[0]['dias']

        cursos = cursos.sort_values(by="nome_curso", ascending=True)
        professores = professores.sort_values(by="nome_professor", ascending=True)
        modalidades = modalidades.sort_values(by="nome_modalidade", ascending=True)
        periodos_df = periodos_df.sort_values(by="nome_periodo", ascending=True)

        return professores, cursos, periodos_df, horarios, dias, modalidades

    # Carregar arquivos JSON do diretório de horários
    def carregar_arquivos_horarios():
        dados = {}  
        cursos = fetch_collection_data("ipog", "cursos")
        for curso in cursos:
            course_name = curso["nome_curso"]
            colecao = f'alocacoes_{course_name.replace(" ", "_").lower()}'
            dados_colecao =  fetch_collection_data("ipog", colecao)
            if dados_colecao: 
                dados[colecao] = dados_colecao[0]
        return dados

    def carregar_arquivos_horarios_ciclo(ciclo):
        dados = {}  
        cursos = fetch_collection_data("ipog", "cursos")
        for curso in cursos:
            course_name = curso["nome_curso"]
            colecao = f'alocacoes_{course_name.replace(" ", "_").lower()}'
            if colecao.endswith(ciclo):
                dados_colecao =  fetch_collection_data("ipog", colecao)[0]
                dados[colecao] = dados_colecao 
        return dados
    
    # Criar uma tabela de horários vazia
    def create_schedule_table():
        schedule = pd.DataFrame("", index=horarios, columns=dias)
        return schedule

    # Consolidar alocações de um professor específico
    def consolidar_horarios_professor(dados, professor_selecionado, curso_selecionado=None):

        tabela_professor = create_schedule_table()
        
        for curso, dados_json in dados.items():
            if curso_selecionado and curso != curso_selecionado:
                continue  

            if "periodos" in dados_json:
                for alocacoes in dados_json["periodos"].values():
                    for alocacao in alocacoes:
                        if alocacao["professor"] == professor_selecionado:
                            disciplina = alocacao["disciplina"]
                            horario = alocacao["horario"]
                            dia = alocacao["dia"]
                            modalidade = alocacao["modalidade"]
                            
                            conteudo = f"{disciplina} ({modalidade})"
                            if conteudo not in tabela_professor.loc[horario, dia]:
                                if tabela_professor.loc[horario, dia]:
                                    tabela_professor.loc[horario, dia] += f"</br>{conteudo}"
                                else:
                                    tabela_professor.loc[horario, dia] = conteudo
        return tabela_professor

    # CSS para a tabela visualizada
    def adicionar_css_customizado():
        st.markdown(
            """
            <style>
            .schedule-table {
                table-layout: fixed;
                width: 100%;
                word-wrap: break-word;
                border-collapse: collapse;
                font-size: 10px; 
            }
            .schedule-table th, .schedule-table td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
                vertical-align: top;
                width: 100px;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .schedule-table th {
                background-color: #f2f2f2;
            }
            
            .schedule {
                background-color: #f2f2f2;
                font-size: 10px; 
                border-radius: 10px;
                text-align: center;
            }
            """,
            unsafe_allow_html=True
        )

    def transformar_texto_curso(curso_selecionado):
        curso_selecionado = curso_selecionado.replace("alocacoes_", "")
        curso_selecionado = curso_selecionado.replace("_", " ")
        curso_selecionado = " ".join(
            palavra.capitalize() if palavra.lower() not in ["de", "do", "da", "e"] else palavra 
            for palavra in curso_selecionado.split()
        )
        return curso_selecionado
    
    # Gerar o PDF da tabela consolidada do professor
    def gerar_pdf_tabela(tabela_professor, professor_selecionado, curso_selecionado=None, ciclo=None):

        titulo = f"Horário Consolidado"

        if curso_selecionado:
            curso_selecionado = transformar_texto_curso(curso_selecionado)
            titulo += f" do curso {curso_selecionado}"
        if ciclo:
            titulo += f" ({ciclo})"

        titulo += f" do(a) Professor(a): {professor_selecionado}"


        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12px; 
                }}
                .schedule-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .schedule-table th, .schedule-table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: center;
                    width: 100px;
                    word-wrap: break-word;
                    white-space: pre-wrap;
                }}
                .schedule-table th {{
                    background-color: #f2f2f2;
                }}
                /* Estilização para as colunas de Sexta, Sábado e Domingo */
                .schedule-table th:nth-child(6), /* Sexta */
                .schedule-table th:nth-child(7), /* Sábado */
                .schedule-table th:nth-child(8), /* Domingo */
                .schedule-table td:nth-child(6),
                .schedule-table td:nth-child(7),
                .schedule-table td:nth-child(8) {{
                    background-color: #F5F5DC;
                }}
            </style>
        </head>
        <body>
            <h2>{titulo}</h2>
           {tabela_professor.to_html(classes="schedule-table", escape=False)}

        </body>
        </html>
        """

        
        return html


    # Exibir a tabela consolidada do professor
    def exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado, curso_selecionado=None, ciclo=None):
        titulo = f"**Horários Consolidados do Professor: {professor_selecionado}**"
        
        if curso_selecionado:
            curso_selecionado = transformar_texto_curso(curso_selecionado)
            titulo += f" - Curso: {curso_selecionado}"
        st.write(titulo)
        st.write(tabela_professor.to_html(escape=False, classes="schedule-table"), unsafe_allow_html=True)


        if st.button("Baixar Horário"):
            html = gerar_pdf_tabela(tabela_professor, professor_selecionado, curso_selecionado, ciclo)
            html_bytes = html.encode('utf-8')
            st.download_button(
                label="Baixar HTML",
                data=html_bytes,
                file_name=f"{professor_selecionado}_horario.html",
                mime="text/html"
    )


#####################################################################################################################################

    st.title("👨‍🏫 :blue[Mostrar Horário do Professor]")
    st.divider()

    # Carregar tabelas e dados básicos
    professores, _, _, horarios, dias, _ = carregar_tabelas()
    adicionar_css_customizado()


    professor_selecionado = st.selectbox("Selecione o professor", professores['nome_professor'])
    tipo_consolidado = st.radio("Escolha o tipo de consolidado:", ("Consolidado Geral", "Consolidado Geral 1 Ciclo","Consolidado Geral 2 Ciclo", "Consolidado por Curso"))

    if tipo_consolidado == "Consolidado Geral":
        dados = carregar_arquivos_horarios()
        tabela_professor = consolidar_horarios_professor(dados, professor_selecionado)
        exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado)

    elif tipo_consolidado == "Consolidado Geral 1 Ciclo":
        dados = carregar_arquivos_horarios_ciclo("_1_ciclo")
        tabela_professor = consolidar_horarios_professor(dados, professor_selecionado)
        exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado, None, "1º Ciclo")

    elif tipo_consolidado == "Consolidado Geral 2 Ciclo":
        dados = carregar_arquivos_horarios_ciclo("_2_ciclo")
        tabela_professor = consolidar_horarios_professor(dados, professor_selecionado)
        exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado, None, "2º Ciclo")
    else:
        dados = carregar_arquivos_horarios()
        curso_selecionado = st.selectbox("Selecione o curso", list(dados.keys()))
        tabela_professor = consolidar_horarios_professor(dados, professor_selecionado, curso_selecionado)
        exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado, curso_selecionado)
