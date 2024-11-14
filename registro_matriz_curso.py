import streamlit as st
import pandas as pd
import json

def app():
    # Função para carregar os cursos a partir do arquivo JSON
    def carregar_cursos():
        caminho_arquivo = f'dados/cursos.json'
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Função para converter o dataframe em formato JSON
    def converter_para_json(df, nome_curso):
        disciplinas = []
        for _, row in df.iterrows():
            disciplinas.append({
                "id_curso": int(row['id_curso']),
                "nome_curso": nome_curso,
                "id_disciplina": int(row['id_disciplina']),
                "nome_disciplina": row['nome_disciplina'],
                "periodo": row['periodo'],
                "carga_horaria": int(row['carga_horaria'])
            })
        return {"disciplinas": disciplinas}

    # Carregar os cursos
    cursos = carregar_cursos()
    nomes_cursos = [curso['nome_curso'] for curso in cursos['cursos']]

    # Título da página
    st.title('Carga da Matriz de Curso')

    # Selecionar o curso
    nome_curso = st.selectbox("Selecione o Curso", nomes_cursos)

    # Upload do arquivo Excel
    arquivo_excel = st.file_uploader("Envie o arquivo Excel", type=["xlsx"])

    # Ler o Excel e exibir como tabela
    if arquivo_excel:
        df = pd.read_excel(arquivo_excel)
        st.write("Pré-visualização dos dados:")
        st.dataframe(df)

        # Botão para converter o Excel em JSON
        if st.button("Converter e Salvar JSON"):
            dados_json = converter_para_json(df, nome_curso)

            nome_arquivo_json = f'matrizes/disciplinas_{nome_curso.replace(" ", "_").lower()}.json'
            with open(nome_arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, indent=4, ensure_ascii=False)

            st.success(f"Arquivo JSON salvo como: {nome_arquivo_json}")

            st.json(dados_json)
