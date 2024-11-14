import streamlit as st
import gerar_com_ia
import registro_agenda
import conflito_entre_cursos
import horario_professor
import registro_dados_comuns
import registro_matriz_curso
from streamlit_option_menu import option_menu

# Configura o layout da página
st.set_page_config(layout="wide")


# Menu à esquerda com option_menu
with st.sidebar:
    selected = option_menu(
        "Menu", 
        ["Montar Horário", "Conflitos entre Cursos", "Horário dos Professores", "Dados Comuns", "Matriz do Curso"], 
        icons=["calendar", "calendar", "calendar", "database", "clipboard-data"], 
        menu_icon="cast", 
        default_index=0
    )

# Carregar a página correspondente com base na opção selecionada
if selected == "Montar Horário":
    registro_agenda.app()
elif selected == "Conflitos entre Cursos":
    conflito_entre_cursos.app()
elif selected == "Horário dos Professores":
    horario_professor.app()
elif selected == "Dados Comuns":
    registro_dados_comuns.app()
elif selected == "Matriz do Curso":
    registro_matriz_curso.app()
