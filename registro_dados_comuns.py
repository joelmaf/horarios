import streamlit as st
import json
import os

def app():
    # Função para carregar dados de um arquivo JSON
    def carregar_dados(nome_arquivo):
        caminho_arquivo = f'dados/{nome_arquivo}'
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)

    # Função para salvar dados em um arquivo JSON
    def salvar_dados(nome_arquivo, dados):
        caminho_arquivo = f'dados/{nome_arquivo}'
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    # Interface do Streamlit
    st.title("📂:blue[Registro de Dados Comuns]")
    st.divider()

    # Selecionar arquivo para trabalhar
    arquivo_selecionado = st.selectbox("Selecione o arquivo JSON", [
        'cursos.json', 'dias.json', 'horarios.json', 'modalidade.json', 'periodos.json', 'professores.json'
    ])

    # Carregar o arquivo selecionado
    caminho_arquivo = f'{arquivo_selecionado}'
    dados = carregar_dados(caminho_arquivo)

    # Função para adicionar novo registro em cursos.json
    def adicionar_curso():
        st.subheader("Adicionar Novo Curso")
        id_curso = st.number_input("ID do Curso", min_value=1)
        nome_curso = st.text_input("Nome do Curso")
        if st.button("Adicionar Curso"):
            dados['cursos'].append({"id_curso": id_curso, "nome_curso": nome_curso})
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Curso '{nome_curso}' adicionado com sucesso!")

    # Função para adicionar novo registro em dias.json
    def adicionar_dia():
        st.subheader("Adicionar Novo Dia")
        novo_dia = st.text_input("Nome do Dia")
        if st.button("Adicionar Dia"):
            dados['dias'].append(novo_dia)
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Dia '{novo_dia}' adicionado com sucesso!")

    # Função para adicionar novo registro em horários.json
    def adicionar_horario():
        st.subheader("Adicionar Novo Horário")
        novo_horario = st.text_input("Digite o novo horário")
        if st.button("Adicionar Horário"):
            dados['horarios'].append(novo_horario)
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Horário '{novo_horario}' adicionado com sucesso!")

    # Função para adicionar novo registro em modalidade.json
    def adicionar_modalidade():
        st.subheader("Adicionar Nova Modalidade")
        id_modalidade = st.number_input("ID da Modalidade", min_value=1)
        modalidade = st.text_input("Nome da Modalidade")
        if st.button("Adicionar Modalidade"):
            dados['modalidade'].append({"id_modalidade": id_modalidade, "modalidade": modalidade})
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Modalidade '{modalidade}' adicionada com sucesso!")

    # Função para adicionar novo registro em períodos.json
    def adicionar_periodo():
        st.subheader("Adicionar Novo Período")
        id_periodo = st.number_input("ID do Período", min_value=1)
        nome_periodo = st.text_input("Nome do Período")
        if st.button("Adicionar Período"):
            dados['periodos'].append({"id_periodo": id_periodo, "nome_periodo": nome_periodo})
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Período '{nome_periodo}' adicionado com sucesso!")

    # Função para adicionar novo registro em professores.json
    def adicionar_professor():
        st.subheader("Adicionar Novo Professor")
        id_professor = st.number_input("ID do Professor", min_value=1)
        nome_professor = st.text_input("Nome do Professor")
        matricula = st.number_input("Matrícula do Professor", min_value=1)
        if st.button("Adicionar Professor"):
            dados['professores'].append({"id_professor": id_professor, "nome_professor": nome_professor, "matricula": matricula})
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Professor '{nome_professor}' adicionado com sucesso!")

    # Escolha do tipo de operação
    operacao = st.selectbox("Selecione a operação", ["Adicionar", "Excluir"])

    # Função para excluir um registro
    def excluir_registro(chave, indice):
        if indice < len(dados[chave]):
            dados[chave].pop(indice)
            salvar_dados(caminho_arquivo, dados)
            st.success(f"Registro de índice {indice} excluído com sucesso!")

    # Executar a operação com base no arquivo selecionado
    if arquivo_selecionado == 'cursos.json':
        if operacao == "Adicionar":
            adicionar_curso()
        elif operacao == "Excluir":
            indice_excluir = st.number_input("Índice do curso a excluir", min_value=0)
            if st.button("Excluir Curso"):
                excluir_registro('cursos', indice_excluir)

    elif arquivo_selecionado == 'dias.json':
        if operacao == "Adicionar":
            adicionar_dia()
        elif operacao == "Excluir":
            indice_excluir = st.number_input("Índice do dia a excluir", min_value=0)
            if st.button("Excluir Dia"):
                excluir_registro('dias', indice_excluir)

    elif arquivo_selecionado == 'horarios.json':
        if operacao == "Adicionar":
            adicionar_horario()
        elif operacao == "Excluir":
            indice_excluir = st.number_input("Índice do horário a excluir", min_value=0)
            if st.button("Excluir Horário"):
                excluir_registro('horarios', indice_excluir)

    elif arquivo_selecionado == 'modalidade.json':
        if operacao == "Adicionar":
            adicionar_modalidade()
        elif operacao == "Excluir":
            indice_excluir = st.number_input("Índice da modalidade a excluir", min_value=0)
            if st.button("Excluir Modalidade"):
                excluir_registro('modalidade', indice_excluir)

    elif arquivo_selecionado == 'periodos.json':
        if operacao == "Adicionar":
            adicionar_periodo()
        elif operacao == "Excluir":
            indice_excluir = st.number_input("Índice do período a excluir", min_value=0)
            if st.button("Excluir Período"):
                excluir_registro('periodos', indice_excluir)

    elif arquivo_selecionado == 'professores.json':
        if operacao == "Adicionar":
            adicionar_professor()
        elif operacao == "Excluir":
            indice_excluir = st.number_input("Índice do professor a excluir", min_value=0)
            if st.button("Excluir Professor"):
                excluir_registro('professores', indice_excluir)


    # Exibir os dados
    st.subheader("Dados atuais")
    st.json(dados)
