import streamlit as st
import os
import json

def app():
    def verificar_conflitos_entre_cursos(diretorio_horarios):
        # Dicionário para armazenar os horários de cada professor
        horarios_professores = {}

        # Iterar por todos os arquivos JSON no diretório
        for arquivo in os.listdir(diretorio_horarios):
            if arquivo.endswith('_alocacoes.json'):
                caminho_arquivo = os.path.join(diretorio_horarios, arquivo)
                
                # Carregar dados do arquivo JSON
                with open(caminho_arquivo, 'r') as json_file:
                    dados = json.load(json_file)
                    nome_curso = dados.get("curso", "Curso desconhecido")
                    
                    # Iterar por períodos e alocações
                    for periodo, alocacoes in dados["periodos"].items():
                        for alocacao in alocacoes:
                            dia = alocacao["dia"]
                            horario = alocacao["horario"]
                            matricula_professor = alocacao["matricula_professor"]
                            nome_professor = alocacao["professor"]

                            # Verificar se o professor já tem um horário no mesmo dia e horário
                            chave_horario = (matricula_professor, nome_professor, dia, horario)
                            
                            if chave_horario in horarios_professores:
                                # Adicionar conflito se já houver um horário para o mesmo professor, dia e horário
                                horarios_professores[chave_horario].append((nome_curso, periodo))
                            else:
                                # Adicionar nova entrada
                                horarios_professores[chave_horario] = [(nome_curso, periodo)]
        
        # Verificar e listar os conflitos encontrados
        conflitos = []
        for chave, cursos in horarios_professores.items():
            if len(cursos) > 1:
                matricula_professor, nome_professor, dia, horario = chave
                conflito_info = {
                    "matricula_professor": matricula_professor,
                    "nome_professor": nome_professor,
                    "dia": dia,
                    "horario": horario,
                    "cursos": cursos
                }
                conflitos.append(conflito_info)
        
        return conflitos

    # Interface Streamlit
    st.title("Verificação de Conflitos de Horário entre Cursos")
    st.write("Essa aplicação verifica se há conflitos de horário entre diferentes cursos para o mesmo professor.")

    # Especifique o diretório onde estão os arquivos JSON de horários
    diretorio_horarios = "horarios"  # Substitua pelo caminho do diretório de horários

    # Botão para iniciar a verificação de conflitos
    if st.button("Verificar Conflitos de Horário"):
        conflitos = verificar_conflitos_entre_cursos(diretorio_horarios)
        
        # Exibir resultados
        if conflitos:
            st.subheader("Conflitos de Horário Detectados:")
            for conflito in conflitos:
                mensagem = f"**Professor {conflito['nome_professor']} (Matrícula {conflito['matricula_professor']})** com conflito no dia **{conflito['dia']}** às **{conflito['horario']}**:"
                st.warning(mensagem)
                for curso, periodo in conflito["cursos"]:
                    st.write(f"- Curso: {curso}, Período: {periodo}")
        else:
            st.success("Nenhum conflito de horário detectado entre os cursos.")
