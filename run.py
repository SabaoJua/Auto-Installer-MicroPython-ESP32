import os
import sys
import subprocess
import time
import platform
import requests
from bs4 import BeautifulSoup
import serial.tools.list_ports


def check_dependencies():
    print("Verificando dependências...")
    
    # Verificar se Python 3 está instalado
    try:
        python_version = subprocess.check_output(["python3", "--version"])
        print(f"Python encontrado: {python_version.decode().strip()}")
    except FileNotFoundError:
        print("Python 3 não encontrado. Instalando Python 3...")
        if system == "Windows":
            os.system("msiexec.exe /i https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe /quiet InstallAllUsers=1 PrependPath=1")
        else:
            os.system("sudo apt install python3 -y")
    
    # Verificar se esptool está instalado
    try:
        subprocess.check_output([sys.executable, "-m", "esptool", "--help"])
        print("Biblioteca esptool encontrada.")
    except subprocess.CalledProcessError:
        print("Biblioteca esptool não encontrada. Instalando esptool...")
        os.system(f"{sys.executable} -m pip install esptool")

def list_firmware_versions():
    BASE_URL = "http://micropython.org"
    DOWNLOAD_PAGE = "/download/ESP32_GENERIC/"

    print("Baixando informações de firmware do MicroPython...")
    response = requests.get(BASE_URL + DOWNLOAD_PAGE)
    if response.status_code != 200:
        print("Erro ao baixar o conteúdo da página.")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')
    firmware_links = [a['href'] for a in soup.find_all('a', href=True) if 'ESP32_GENERIC-' in a['href']]

    if not firmware_links:
        print("Nenhuma versão de firmware encontrada.")
        sys.exit(1)

    print("Versões de firmware disponíveis:")
    options = []
    for idx, link in enumerate(firmware_links, 1):
        full_link = BASE_URL + link
        version = link.split('ESP32_GENERIC-')[1].split('.bin')[0]
        options.append(full_link)
        print(f"{idx}: Versão: {version} - Link: {full_link}")

    selection = int(input("Selecione o número da versão desejada: ")) - 1
    if selection < 0 or selection >= len(options):
        print("Seleção inválida. Por favor, selecione um número válido.")
        return list_firmware_versions()

    selected_firmware = options[selection]
    print(f"Firmware selecionado: {selected_firmware}")

    download_firmware(selected_firmware)

def download_firmware(firmware_url):
    firmware_file = firmware_url.split('/')[-1]
    print(f"Baixando firmware {firmware_file}...")

    response = requests.get(firmware_url)
    if response.status_code == 200:
        with open(firmware_file, 'wb') as file:
            file.write(response.content)
        print(f"Firmware baixado com sucesso: {firmware_file}")
    else:
        print("Erro ao baixar o firmware.")
        sys.exit(1)

    check_dependencies()
    erase_flash()
    install_firmware(firmware_file)

def erase_flash():
    print("Apagando a flash do ESP32...")
    port = find_serial_port()
    if port:
        subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32", "--port", port, "erase_flash"])
        print("Flash do ESP32 apagada com sucesso.")
    else:
        print("Erro ao apagar a flash do ESP32.")
        sys.exit(1)

def install_firmware(firmware_file):
    print(f"Instalando o firmware {firmware_file} no ESP32...")
    port = find_serial_port()
    if port:
        subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32", "--port", port, "--baud", "460800", "write_flash", "-z", "0x1000", firmware_file])
        print("Firmware instalado com sucesso no ESP32.")
    else:
        print("Erro ao instalar o firmware no ESP32.")
        sys.exit(1)

def find_serial_port():
    system = platform.system()

    if system == "Windows":
        ports = [p.device for p in serial.tools.list_ports.comports() if 'USB' in p.description or 'UART' in p.description]
    else:  # Linux e outros sistemas baseados em Unix
        ports = ["/dev/" + p for p in os.listdir('/dev') if p.startswith('ttyUSB') or p.startswith('ttyACM')]

    return ports[0] if ports else None
if __name__ == "__main__":
    system = platform.system()
    
    # Verifica se o usuário está no grupo dialout (apenas para Linux)
    if system != "Windows":
        if 'dialout' not in os.popen('groups').read():
            print("Adicionando usuário ao grupo dialout...")
            os.system("sudo usermod -a -G dialout $USER")
            print("Usuário adicionado ao grupo dialout. Por favor, faça logout e login para aplicar as alterações.")
    
    # Verifica se o brltty está instalado e remove se necessário (apenas para Linux)
    if system != "Windows":
        if 'brltty' in os.popen('dpkg -l').read():
            print("Desinstalando brltty...")
            os.system("sudo apt purge brltty -y")
    
    print("Insira o ESP32 em alguma porta USB...")
    while True:
        port = find_serial_port()
        if port:
            print(f"ESP32 conectado em {port}!")
            list_firmware_versions()
            break
        time.sleep(1)

