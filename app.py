import streamlit as st
import easyocr
import cv2
import numpy as np
import requests
from PIL import Image

# --- CONFIGURAÇÃO ---
# Sua chave já está inserida abaixo
SERPER_API_KEY = "bf6f479db8bb17ab9b8b3be2c0b36caf7bc1c076"

# Inicializa o leitor de OCR (Cache para não carregar toda hora)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['pt', 'en'])

reader = load_ocr()

# --- FUNÇÕES DE APOIO ---

def buscar_imagem_modelo(nome_carro):
    """Busca a imagem oficial do carro no Google via Serper.dev"""
    url = "https://google.serper.dev/images"
    payload = {"q": f"{nome_carro} oficial carro fundo branco", "num": 1}
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        results = response.json()
        if "images" in results and len(results["images"]) > 0:
            return results["images"][0]["imageUrl"]
    except:
        pass
    return "https://via.placeholder.com/400x300.png?text=Imagem+nao+encontrada"

def consultar_dados_placa(placa):
    """
    Simulação de banco de dados. 
    Para qualquer placa fora da lista, ele gera uma busca genérica.
    """
    base_teste = {
        "BRA2E19": "Toyota Corolla 2024 Branco",
        "ABC1234": "Volkswagen Golf GTI Vermelho",
        "PLACA01": "Honda Civic G10 Preto"
    }
    # Se não achar na lista, tenta buscar pelo texto da placa no Google
    return base_teste.get(placa, f"Carro modelo da placa {placa}")

def processar_e_exibir_resultado(placa_texto):
    """Lógica unificada para mostrar o resultado na tela"""
    st.divider()
    col_info, col_img = st.columns(2)
    
    # 1. Identifica o modelo (Simulado ou Real)
    modelo_veiculo = consultar_dados_placa(placa_texto)
    
    # 2. Busca a imagem no Google
    url_imagem = buscar_imagem_modelo(modelo_veiculo)
    
    with col_info:
        st.success(f"### Placa: {placa_texto}")
        st.subheader(f"Modelo sugerido: {modelo_veiculo}")
        st.info("Nota: Para resultados reais de qualquer placa, seria necessário integrar uma API de dados veiculares paga.")
        
    with col_img:
        st.image(url_imagem, caption=f"Resultado da busca para: {modelo_veiculo}", use_container_width=True)

# --- INTERFACE DO SITE ---

st.set_page_config(page_title="Busca Veicular", layout="wide", page_icon="🚗")

st.title("Modelos de carros supimpa")
st.write("Identifique um veículo através da foto da placa ou digitando os caracteres.")

# Criação das abas
aba_foto, aba_texto = st.tabs(["📷 Identificar por Foto", "⌨️ Digitar Placa"])

with aba_foto:
    arquivo = st.file_uploader("Suba a foto da traseira do carro...", type=["jpg", "png", "jpeg"])
    if arquivo:
        img_pil = Image.open(arquivo)
        st.image(img_pil, width=350, caption="Sua Foto")
        
        if st.button("✨ Analisar Foto"):
            with st.spinner("Processando imagem com Visão Computacional..."):
                # Converte para formato OpenCV e lê o texto
                resultados_ocr = reader.readtext(np.array(img_pil))
                if resultados_ocr:
                    # Limpa o texto (remove espaços e traços)
                    placa_lida = resultados_ocr[0][1].upper().replace("-", "").replace(" ", "")
                    processar_e_exibir_resultado(placa_lida)
                else:
                    st.error("Não foi possível detectar caracteres de placa nesta imagem.")

with aba_texto:
    placa_input = st.text_input("Digite a placa (Ex: BRA2E19):").upper().strip()
    if st.button("🔍 Buscar Modelo"):
        if placa_input:
            processar_e_exibir_resultado(placa_input)
        else:
            st.warning("Por favor, insira uma placa válida.")

st.divider()
st.caption("Desenvolvido para fins de estudo em Visão Computacional e APIs.")