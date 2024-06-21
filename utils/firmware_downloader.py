import sys
import time
import requests
import os
from bs4 import BeautifulSoup
import tempfile
from utils.flash_manager import erase_flash, install_firmware

def list_firmware_versions():
    BASE_URL = "http://micropython.org"
    DOWNLOAD_PAGE = "/download/ESP32_GENERIC/"

    print("Baixando informações de firmware do MicroPython...")
    time.sleep(1)
    
    response = requests.get(BASE_URL + DOWNLOAD_PAGE)
    
    if response.status_code != 200:
        print("Erro ao baixar o conteúdo da página.")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    firmware_links = [a['href'] for a in soup.find_all('a', href=True) if 'ESP32_GENERIC-' in a['href'] and a['href'].endswith('.bin')][:10]

    if not firmware_links:
        print("Nenhuma versão de firmware encontrada.")
        sys.exit(1)

    print("===============================================================================")
    print("==       Listando as 10 primeiras Versões de firmware disponíveis:           ==")
    print("===============================================================================")
    time.sleep(0.5)
    
    options = []
    
    for idx, link in enumerate(firmware_links, 1):
        full_link = BASE_URL + link
        options.append(full_link)
        version = link.replace("/resources/firmware/", "")
        print(f"== Nº: {idx} | Versão: {version} ")
        print("-------------------------------------------------------------------------------")

    selection = int(input("Selecione o número da versão desejada: "))
    
    if selection < 0 or selection >= len(options):
        print("Seleção inválida. Por favor, selecione um número válido.")
        return list_firmware_versions()

    selected_firmware = options[selection - 1]
    print("✅ Firmware selecionado com sucesso...")
    time.sleep(1)

    download_firmware(selected_firmware)

def download_firmware(firmware_url):
    firmware_file = firmware_url.split('/')[-1]
    print("⌛ Baixando firmware...")

    response = requests.get(firmware_url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(response.content)
            temp_file_name = tmpfile.name
            
        print("✅ Firmware baixado com sucesso:")
        print("-------------------------------------------------------------------------------")
        time.sleep(1)
    else:
        print("Erro ao baixar o firmware.")
        sys.exit(1)

    erase_flash()
    install_firmware(temp_file_name)
    os.remove(temp_file_name)
