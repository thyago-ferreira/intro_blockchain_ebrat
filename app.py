import streamlit as st
import hashlib
from web3 import Web3
import json
from datetime import datetime
import pandas as pd
import os
import base64

# ================= CONFIGURAÇÕES =================
CONTRATO_ENDERECO = "" # <--- SEU ENDEREÇO DE CONTRATO AQUI
PRIVATE_KEY = "" # <--- SUA CHAVE AQUI
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
# =================================================

st.set_page_config(page_title="eBRAT - PMERJ", page_icon="👮", layout="wide")

# ---------- Utilidades ----------
def get_base64_image(image_path: str) -> str:
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

img_brasao = get_base64_image("brasao.png")
img_ebrat  = get_base64_image("logo_ebrat.png")

# ---------- CSS FINAL ----------
st.markdown("""
<style>
    /* 1. RESET */
    header[data-testid="stHeader"] {display:none;}
    .block-container {
        padding-top: 1rem; padding-bottom: 5rem;
        padding-left: 2rem; padding-right: 2rem;
    }
    .stApp {background-color: #FFFFFF;}
    
    h1, h2, h3, p, li, div, span, label {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #212529;
    }

    /* 2. ALERTAS (FLAT) */
    div[data-testid="stAlert"] {
        padding: 15px;
        border-radius: 6px;
        border: none !important;
        margin-bottom: 15px;
    }
    div[data-testid="stNotification"] { background-color: #d1ecf1 !important; color: #0c5460 !important; }
    div[data-testid="stAlert"] { background-color: #fff3cd !important; color: #856404 !important; }
    
    div[data-testid="stAlert"] p { color: inherit !important; }
    div[data-testid="stAlert"] svg { fill: currentColor !important; }

    /* 3. FILE UPLOADER (ESTILO ESCURO) */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #1a1a1a !important;
        border: 1px dashed #555 !important;
        border-radius: 6px !important;
        padding: 10px 20px !important;
        min-height: auto !important;
        align-items: center;
        display: flex;
        flex-direction: row;
        gap: 15px;
    }

    /* Ícone */
    [data-testid="stFileUploaderDropzone"] svg {
        fill: #ffffff !important;
        width: 24px !important; height: 24px !important; margin: 0 !important;
    }
    [data-testid="stFileUploaderDropzone"] > div:first-child { margin: 0 !important; padding: 0 !important; width: auto !important; }

    /* Textos Customizados */
    [data-testid="stFileUploaderDropzone"] div div::before, [data-testid="stFileUploaderDropzone"] section > div > div > span, [data-testid="stFileUploaderDropzone"] small {display: none;}

    [data-testid="stFileUploaderDropzone"] section > div > div::after {
        content: "Arraste e solte o PDF do eBRAT aqui";
        color: #ffffff !important;
        font-weight: 500; font-size: 14px; white-space: nowrap;
    }
    [data-testid="stFileUploaderDropzone"] section::after {
        content: "(Max: 200MB)";
        font-size: 12px; color: #888888 !important; margin-top: 2px;
    }

    /* 4. BOTÃO BROWSE FILES (BRANCO) */
    button[data-testid="baseButton-secondary"] {
        color: #ffffff !important;        
        border-color: #ffffff !important; 
        background-color: transparent !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        height: auto !important;
        padding: 4px 12px !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        color: #F7941D !important;
        border-color: #F7941D !important;
        background-color: rgba(255,255,255,0.1) !important;
    }

    /* 5. REMOÇÃO DA LISTA DE UPLOAD (OK) */
    [data-testid="stUploadedFile"], 
    section[data-testid="stFileUploader"] ul,
    section[data-testid="stFileUploader"] li,
    div[data-testid="stFileUploader"] > div > div:nth-child(2) {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* 6. BOTÕES PRINCIPAIS */
    .stButton > button {
        background-color: #F7941D !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 0 !important;
        width: 100%;
        text-transform: uppercase;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button:hover {
        background-color: #d67d10 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* 7. ABAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #eee;
        margin-bottom: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #0092dd;
        font-weight: 600;
        border: none;
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #005a8d;
        border-bottom: 3px solid #005a8d;
    }

    /* 8. RODAPÉ */
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #333; color: #fff;
        text-align: center; padding: 10px;
        font-size: 12px; z-index: 9999;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Cabeçalho ----------
st.markdown(f"""
<div style="
    background-color: #0092dd;
    padding: 10px 40px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    margin-bottom: 20px;
">
    <img src="data:image/png;base64,{img_brasao}" style="height: 50px; width: auto;">
    <div style="border-left: 1px solid rgba(255,255,255,0.3); height: 35px;"></div>
    <img src="data:image/png;base64,{img_ebrat}" style="height: 30px; width: auto;">
</div>
""", unsafe_allow_html=True)

# ---------- Web3 ----------
w3 = Web3(Web3.HTTPProvider(RPC_URL))
try: 
    conta_do_oficial = w3.eth.account.from_key(PRIVATE_KEY).address
except: 
    conta_do_oficial = None

ABI = '[{"inputs":[{"internalType":"bytes32","name":"_hash","type":"bytes32"}],"name":"registrarDocumento","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"_hash","type":"bytes32"}],"name":"verificarDocumento","outputs":[{"internalType":"bool","name":"","type":"bool"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]'

def gerar_hash(arquivo) -> str:
    return "0x" + hashlib.sha256(arquivo.getvalue()).hexdigest()

def salvar_historico_local(nome: str, hash_doc: str):
    dados = {
        "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
        "Arquivo (eBRAT)": [nome],
        "Hash (ID Blockchain)": [hash_doc],
    }
    df = pd.DataFrame(dados)
    if not os.path.isfile("historico_ebrats.csv"):
        df.to_csv("historico_ebrats.csv", index=False)
    else:
        df.to_csv("historico_ebrats.csv", mode="a", header=False, index=False)

# ---------- Tabs ----------
aba1, aba2 = st.tabs(["🔍 CONSULTA PÚBLICA", "🔐 SISTEMA DE REGISTRO"])

# ===================== CONSULTA =====================
with aba1:
    # Alerta Info Customizado
    st.markdown("""
    <div style="background-color: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-size: 14px;">
        ℹ️ Utilize o campo abaixo para verificar a autenticidade e integridade do eBRAT na Blockchain.
    </div>
    """, unsafe_allow_html=True)
    
    file = st.file_uploader("Selecione o arquivo", type=["pdf"], key="consulta", label_visibility="collapsed")

    if file:
        # Card Arquivo
        st.markdown(f"""
        <div style="background:#f8f9fa; padding:10px 15px; border-radius:6px; border:1px solid #ddd; border-left:5px solid #0092dd; margin-top:5px; margin-bottom:5px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <p style="margin:0; font-size:14px; color:#333; font-weight:600;">📄 {file.name}</p>
                <span style="font-size:12px; color:#777; background:#eee; padding:2px 6px; border-radius:4px;">{(file.size/1024):.1f} KB</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("CONSULTAR BASE DE DADOS"):
            contrato = w3.eth.contract(address=CONTRATO_ENDERECO, abi=json.loads(ABI))
            hash_check = gerar_hash(file)
            
            with st.spinner('Verificando...'):
                try:
                    existe, ts, emissor = contrato.functions.verificarDocumento(hash_check).call()
                    
                    if existe:
                        data_fmt = datetime.fromtimestamp(ts).strftime("%d/%m/%Y às %H:%M")
                        st.success("✅ Documento Autêntico")
                        st.markdown(f"""
                        <div style="background:#f0fff4; border:1px solid #c3e6cb; padding:15px; border-radius:8px; margin-top:5px;">
                            <h4 style="color:#28a745; margin-top:0; font-size:16px;">🛡️ Certificado de Validade</h4>
                            <hr style="border-top:1px solid #c3e6cb; margin: 8px 0;">
                            <p style="margin-bottom:4px; font-size:14px;"><b>📅 Data:</b> {data_fmt}</p>
                            <p style="margin-bottom:4px; font-size:14px;"><b>🔑 Hash:</b> {hash_check[:20]}...</p>
                            <p style="margin:0; font-size:13px; color:#555;"><b>✍️ Oficial:</b> {emissor}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Erro Customizado
                        st.markdown("""
                        <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; margin-top: 10px;">
                            ❌ <b>Documento não encontrado ou alterado.</b>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Erro: {e}")

# ===================== REGISTRO =====================
with aba2:
    # Alerta Warning Customizado
    st.markdown("""
    <div style="background-color: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-size: 14px;">
        ⚠️ <b>Atenção Oficial:</b> O registro em Blockchain é uma operação irreversível e gera custos (Gas). Certifique-se de que o arquivo é a versão final.
    </div>
    """, unsafe_allow_html=True)

    file_reg = st.file_uploader("Selecione o arquivo", type=["pdf"], key="registro", label_visibility="collapsed")

    if file_reg:
        st.markdown(f"""
        <div style="background:#fff3cd; padding:10px 15px; border-radius:6px; border:1px solid #ffeeba; border-left:5px solid #F7941D; margin-top:5px; margin-bottom:5px;">
             <p style="margin:0; font-size:14px; color:#856404; font-weight:600;">📄 Pronto para registro: {file_reg.name}</p>
        </div>
        """, unsafe_allow_html=True)

        hash_doc = gerar_hash(file_reg)
        
        if st.button("REGISTRAR NA BLOCKCHAIN"):
            if conta_do_oficial is None:
                st.error("❌ Erro: Chave Privada não configurada no código.")
            else:
                try:
                    contrato = w3.eth.contract(address=CONTRATO_ENDERECO, abi=json.loads(ABI))
                    with st.spinner("Registrando..."):
                        nonce = w3.eth.get_transaction_count(conta_do_oficial, "pending")
                        tx = contrato.functions.registrarDocumento(hash_doc).build_transaction({
                            "chainId": 11155111, "gas": 200000, "gasPrice": w3.eth.gas_price, "nonce": nonce
                        })
                        signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
                        salvar_historico_local(file_reg.name, hash_doc)

                    st.success("✅ Registro realizado!")
                    
                    # Link Etherscan CORRIGIDO com 0x na frente
                    st.markdown(f"""
                    <a href="https://sepolia.etherscan.io/tx/0x{tx_hash.hex()}" target="_blank" style="text-decoration:none;">
                        <div style="background:#003366; color:white; padding:8px; border-radius:6px; text-align:center; font-weight:bold; margin-top:5px; font-size:14px;">
                            🔗 Visualizar no Etherscan
                        </div>
                    </a>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Erro: {e}")

    st.divider()
    
    st.markdown("<h5 style='margin-bottom:10px;'>📂 Histórico Local</h5>", unsafe_allow_html=True)
    if os.path.isfile("historico_ebrats.csv"):
        df = pd.read_csv("historico_ebrats.csv")
        st.dataframe(df, use_container_width=True, hide_index=True)

# ---------- Rodapé ----------
st.markdown("""
<div class="footer">
    Site oficial da Secretaria de Estado de Polícia Militar - Rio de Janeiro | Copyright 2025 | Desenvolvido pela DSI
</div>
""", unsafe_allow_html=True)
