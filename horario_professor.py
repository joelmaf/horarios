import streamlit as st
import pandas as pd
import json
import os
from openpyxl import Workbook
import pdfkit
import io
import tempfile

def app():
    
    # Função para carregar arquivos JSON
    def carregar_json(arquivo):
        if os.path.exists(arquivo):
            with open(arquivo, 'r') as json_file:
                return json.load(json_file)
        return None

    # Carregar professores, cursos, períodos e horários de arquivos JSON
    def carregar_tabelas():
        professores_json = carregar_json('dados/professores.json')
        cursos_json = carregar_json('dados/cursos.json')
        periodos_json = carregar_json('dados/periodos.json')
        horarios_json = carregar_json('dados/horarios.json')
        dias_json = carregar_json('dados/dias.json')
        modalidades_json = carregar_json('dados/modalidade.json')

        professores = pd.DataFrame(professores_json['professores'])
        cursos = pd.DataFrame(cursos_json['cursos'])
        periodos_df = pd.DataFrame(periodos_json['periodos'])
        horarios = horarios_json['horarios']
        dias = dias_json['dias']
        modalidades = pd.DataFrame(modalidades_json['modalidade'])

        return professores, cursos, periodos_df, horarios, dias, modalidades

    # Carregar arquivos JSON do diretório de horários
    def carregar_arquivos_horarios(diretorio="horarios"):
        dados = {}  
        for arquivo in os.listdir(diretorio):
            if arquivo.endswith("_alocacoes.json"):
                curso_nome = arquivo.replace("_alocacoes.json", "").replace("_", " ").title()
                caminho_arquivo = os.path.join(diretorio, arquivo)
                with open(caminho_arquivo, 'r') as json_file:
                    dados_json = json.load(json_file)
                    dados[curso_nome] = dados_json 
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
                                    tabela_professor.loc[horario, dia] += f"\n{conteudo}"
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

    # Gerar o PDF da tabela consolidada do professor
    def gerar_pdf_tabela(tabela_professor, professor_selecionado, curso_selecionado=None):

        titulo = f"Horário Consolidado do(a) Professor(a): {professor_selecionado}"

        if curso_selecionado:
            titulo += f" - Curso: {curso_selecionado}"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 8px; 
                }}
                .schedule-table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .schedule-table th, .schedule-table td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
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
        #pdf_file = f"{professor_selecionado}_horarios.pdf" if not curso_selecionado else f"{professor_selecionado}_{curso_selecionado}_horarios.pdf"
        #pdfkit.from_string(html, pdf_file)
        #return pdf_file

        # Cria um arquivo temporário para o PDF e lê para o buffer de memória
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp_pdf:
            pdfkit.from_string(html, tmp_pdf.name)
            tmp_pdf.seek(0)  # Retorna ao início do arquivo temporário
            pdf_buffer = io.BytesIO(tmp_pdf.read())  # Lê o conteúdo para BytesIO
        
        pdf_buffer.seek(0)  # Retorna ao início do buffer
        return pdf_buffer


    # Exibir a tabela consolidada do professor
    def exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado, curso_selecionado=None):
        titulo = f"**Horários Consolidados do Professor: {professor_selecionado}**"
        
        if curso_selecionado:
            titulo += f" - Curso: {curso_selecionado}"
        st.write(titulo)
        st.write(tabela_professor.to_html(escape=False, classes="schedule-table"), unsafe_allow_html=True)

        if st.button("Baixar PDF"):
            pdf_buffer = gerar_pdf_tabela(tabela_professor, professor_selecionado, curso_selecionado)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name=f"{professor_selecionado}_horarios.pdf",
                mime="application/pdf"
            )


#####################################################################################################################################

    # Carregar tabelas e dados básicos
    professores, _, _, horarios, dias, _ = carregar_tabelas()
    adicionar_css_customizado()

    # Carregar todos os dados de horários dos arquivos no diretório
    dados = carregar_arquivos_horarios()

    professor_selecionado = st.selectbox("Selecione o professor", professores['nome_professor'])
    tipo_consolidado = st.radio("Escolha o tipo de consolidado:", ("Consolidado Geral", "Consolidado por Curso"))

    if tipo_consolidado == "Consolidado Geral":
        tabela_professor = consolidar_horarios_professor(dados, professor_selecionado)
        exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado)
    else:
        curso_selecionado = st.selectbox("Selecione o curso", list(dados.keys()))
        tabela_professor = consolidar_horarios_professor(dados, professor_selecionado, curso_selecionado)
        exibir_tabela_professor_consolidada(tabela_professor, professor_selecionado, curso_selecionado)
