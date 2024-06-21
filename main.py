import os
import sys
import time
import platform
from utils.firmware_downloader import list_firmware_versions
from utils.port_finder import find_serial_port
from utils.messages import HEADER_TEXT

def print_header():
    print(HEADER_TEXT)

if __name__ == "__main__":
    print_header()
    system = platform.system()
    
    # Verificações específicas para Linux
    if system != "Windows":
        # Verifica se o usuário está no grupo dialout
        if 'dialout' not in os.popen('groups').read():
            print("Para prosseguir, precisamos adicionar o usuário ao grupo dialout.")
            dialout_response = input("Você deseja prosseguir? Digite [Y] para sim ou [N] para não: ")
            
            if dialout_response.lower() not in ['y', 'yes']:
                print("Encerrando o script...")
                sys.exit(1)
            
            print("Adicionando usuário ao grupo dialout...")
            os.system("sudo usermod -a -G dialout $USER")
            print("Usuário adicionado ao grupo dialout. Por favor, faça logout e login para aplicar as alterações.")
        
        # Verifica se o pacote brltty está instalado
        if 'brltty' in os.popen('dpkg -l').read():
            print("Para prosseguir, precisamos desinstalar o pacote brltty.")
            dialout_response = input("Você deseja prosseguir? Digite [Y] para sim ou [N] para não: ")
            
            if dialout_response.lower() not in ['y', 'yes']:
                print("Encerrando o script...")
                sys.exit(1)
            
            print("Desinstalando brltty...")
            os.system("sudo apt purge brltty -y")
    
    print("Insira o ESP32 em alguma porta USB... ")
    while True:
        port = find_serial_port()
        if port:
            print("Conectando...")
            time.sleep(2)
            print(f"ESP32 conectado em {port}!")
            print("----------------------------------------")
            time.sleep(1)
            list_firmware_versions()
            break
        time.sleep(1)
