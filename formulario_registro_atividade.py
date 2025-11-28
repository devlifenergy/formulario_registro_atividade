# app_registro_atividades_v3.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
import hashlib
import urllib.parse
import hmac

# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6"
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Formulário 4 - Registro de Atividades",
    layout="wide"
)

# --- CSS CUSTOMIZADO ---
st.markdown(f"""
    <style>
        div[data-testid="stHeader"], div[data-testid="stDecoration"] {{
            visibility: hidden; height: 0%; position: fixed;
        }}
        
        #autoclick-div {{
            display: none !important; 
        }}
        
        footer {{ visibility: hidden; height: 0%; }}
        .stApp {{ background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT_DARK}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT_DARK}; }}
        .stApp > header {{
            background-color: {COLOR_PRIMARY}; padding: 1rem;
            border-bottom: 5px solid {COLOR_TEXT_DARK};
        }}
        div.st-emotion-cache-1r4qj8v {{
             background-color: #f0f2f6; border-left: 5px solid {COLOR_PRIMARY};
             border-radius: 5px; padding: 1.5rem; margin-top: 1rem;
             margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        div[data-testid="textInputRootElement"] > label,
        div[data-testid="stTextArea"] > label,
        div[data-testid="stRadioGroup"] > label, 
        div[data-testid="stDateInput"] > label,
        div[data-testid="stSelectbox"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stDateInput"] input,
        div[data-testid="stTextArea"] textarea {{
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: #FFFFFF;
        }}
        .stButton button {{
            background-color: {COLOR_PRIMARY}; color: white; font-weight: bold;
            padding: 0.75rem 1.5rem; border-radius: 8px; border: none;
        }}
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO (SESSION STATE) ---
if 'lista_atividades' not in st.session_state:
    st.session_state.lista_atividades = []

# --- CONEXÃO COM GOOGLE SHEETS (COM CACHE) ---
@st.cache_resource
def connect_to_gsheet():
    try:
        creds_dict = dict(st.secrets["google_credentials"])
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        gc = gspread.service_account_from_dict(creds_dict)
        
        # ##### ATUALIZADO: Planilha 'formularios_pessoais', Aba 'instrumento_lifenergy' #####
        spreadsheet = gc.open("formularios_pessoais") 
        return spreadsheet.worksheet("instrumento_lifenergy") 
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return None

ws_respostas = connect_to_gsheet()

if ws_respostas is None:
    st.error("Não foi possível conectar à aba 'instrumento_lifenergy' da planilha 'formularios_pessoais'.")
    st.stop()

# --- CABEÇALHO DA APLICAÇÃO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo_wedja.jpg", width=120)
    except FileNotFoundError:
        st.warning("Logo 'logo_wedja.jpg' não encontrada.")
with col2:
    st.markdown(f"""
    <div style="display: flex; align-items: center; height: 100%;">
        <h1 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>FORMULÁRIO 4 - REGISTRO DE ATIVIDADES</h1>
    </div>
    """, unsafe_allow_html=True)

# --- SEÇÃO DE IDENTIFICAÇÃO ---
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação</h3>", unsafe_allow_html=True)
    
    # --- Validação do Link ---
    org_coletora_valida = "Instituto Wedja de Socionomia"
    link_valido = False 

    try:
        query_params = st.query_params
        org_encoded_from_url = query_params.get("org")
        exp_from_url = query_params.get("exp")
        sig_from_url = query_params.get("sig")
        
        if org_encoded_from_url and exp_from_url and sig_from_url:
            org_decoded = urllib.parse.unquote(org_encoded_from_url)
            secret_key = st.secrets["LINK_SECRET_KEY"].encode('utf-8')
            message = f"{org_decoded}|{exp_from_url}".encode('utf-8')
            calculated_sig = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(calculated_sig, sig_from_url):
                timestamp_validade = int(exp_from_url)
                timestamp_atual = int(datetime.now().timestamp())
                
                if timestamp_atual <= timestamp_validade:
                    link_valido = True
                    org_coletora_valida = org_decoded
                else:
                    st.error("Link Expirado.")
            else:
                st.error("Link inválido ou adulterado.")
        else:
             if not (org_encoded_from_url or exp_from_url or sig_from_url):
                 link_valido = True
             else:
                 st.error("Link inválido.")
    except Exception:
        link_valido = False

    col1_form, col2_form = st.columns(2)
    
    with col1_form:
        nome_completo = st.text_input("Nome Completo:", key="input_nome")
        data_nascimento = st.date_input(
            "Data de Nascimento:",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.now(),
            format="DD/MM/YYYY"
        )
        contato = st.text_input("Contato (Email/Telefone):", key="input_contato")

    with col2_form:
        area_empresa = st.text_input("Área/Empresa:", key="input_empresa")
        funcao_cargo = st.text_input("Função/Cargo:", key="input_cargo")
        st.text_input("Organização Coletora:", value=org_coletora_valida, disabled=True)

if not link_valido:
    st.error("Acesso bloqueado.")
    st.stop()

# --- INSTRUÇÕES ---
with st.expander("Ver Orientações aos Respondentes", expanded=True):
    st.info("Adicione as atividades realizadas. Você pode inserir várias atividades clicando em 'ADICIONAR ATIVIDADE'. Ao terminar, clique em 'Finalizar e Enviar'.")

# --- ÁREA DE REGISTRO DE ATIVIDADES ---
st.subheader("Registro de Atividades")

# Container para entrada de dados
with st.container(border=True):
    col_data, col_tipo = st.columns([1, 2])
    
    with col_data:
        data_ativ = st.date_input("Data da Atividade:", datetime.now(), key="input_data_ativ")
    
    with col_tipo:
        tipo_ativ = st.selectbox(
            "Tipo:", 
            ["Atividade ou Exercício", "Sucesso", "Pensamento"],
            key="input_tipo_ativ"
        )
    
    descricao_ativ = st.text_area("Descrição:", height=100, key="input_desc_ativ")
    obs_ativ = st.text_input("Observações ou Sentimento:", key="input_obs_ativ")

    # Botão para adicionar na lista temporária
    if st.button("ADICIONAR ATIVIDADE", type="secondary"):
        if not descricao_ativ:
            st.warning("Por favor, preencha a descrição da atividade.")
        else:
            nova_atividade = {
                "Data": data_ativ.strftime('%d/%m/%Y'),
                "Tipo": tipo_ativ,
                "Descrição": descricao_ativ,
                "Observações": obs_ativ
            }
            st.session_state.lista_atividades.append(nova_atividade)
            st.success("Atividade adicionada à lista! Adicione mais ou clique em Finalizar.")

# --- VISUALIZAÇÃO DA LISTA ---
if st.session_state.lista_atividades:
    st.markdown("### Atividades Listadas para Envio:")
    df_atividades = pd.DataFrame(st.session_state.lista_atividades)
    st.dataframe(df_atividades, use_container_width=True)
    
    if st.button("Limpar Lista", type="secondary"):
        st.session_state.lista_atividades = []
        st.rerun()

# --- BOTÃO DE FINALIZAR E ENVIAR ---
st.markdown("---")
if st.button("Finalizar e Enviar Todas as Atividades", type="primary"):
    if not st.session_state.lista_atividades:
        st.warning("A lista está vazia. Adicione pelo menos uma atividade antes de enviar.")
    else:
        st.subheader("Enviando Registros...")
        
        with st.spinner("Enviando dados para a planilha..."):
            try:
                timestamp_str = datetime.now().isoformat(timespec="seconds")
                
                # Gera ID da Organização
                nome_limpo = org_coletora_valida.strip().upper()
                id_organizacao = hashlib.md5(nome_limpo.encode('utf-8')).hexdigest()[:8].upper()
                
                rows_to_append = []
                
                # ##### LÓGICA DE ENVIO ATUALIZADA PARA 'instrumento_lifenergy' #####
                for ativ in st.session_state.lista_atividades:
                    
                    # Combina a data com a descrição para não perder a informação
                    descricao_com_data = f"[{ativ['Data']}] {ativ['Descrição']}"

                    rows_to_append.append([
                        timestamp_str,                          # Timestamp
                        id_organizacao,                         # ID_FORMULARIO
                        nome_completo,                          # NOME_COMPLETO
                        data_nascimento.strftime('%d/%m/%Y'),   # DATA_NASC
                        contato,                                # CONTATO
                        area_empresa,                           # AREA_EMPRESA
                        funcao_cargo,                           # FUNCAO
                        ativ["Tipo"],                           # TIPO
                        descricao_com_data,                     # DESCRICAO (Com data)
                        ativ["Observações"]                     # OBS_SENTIMENTO
                    ])

                # Envia todas as linhas de uma vez
                ws_respostas.append_rows(rows_to_append, value_input_option='USER_ENTERED')
                
                st.success(f"{len(rows_to_append)} atividades registradas com sucesso!")
                st.session_state.lista_atividades = [] # Limpa a lista após envio
                st.balloons()
                
            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")

# --- BOTÃO INVISÍVEL PARA PINGER ---
placeholder = st.empty()
with placeholder:
    st.markdown('<div id="autoclick-div">', unsafe_allow_html=True) 
    if st.button("Ping Button", key="autoclick_button"):
        print("Ping button clicked by automation.")
    st.markdown('</div>', unsafe_allow_html=True)