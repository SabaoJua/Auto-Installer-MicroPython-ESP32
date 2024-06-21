import sys
import time
import esptool
from utils.port_finder import find_serial_port  
from utils.messages import FOOTER_TEXT

def erase_flash():
    print("  ⌛ Iniciando a Remoção da Flash do ESP...")
    print("-------------------------------------------------------------------------------")
    time.sleep(1)
    port = find_serial_port()
    
    if port:
        try:
            esptool.main(["--chip", "esp32", "--port", port, "erase_flash"])
            print("-------------------------------------------------------------------------------")
            print("  ✅ Flash apagada com sucesso. ✅")
            print("-------------------------------------------------------------------------------")
            time.sleep(1)
        except Exception as e:
            print(f"Erro ao apagar a flash do ESP32: {e}")
            sys.exit(1)
    else:
        print("Erro ao encontrar a porta serial do ESP32.")
        sys.exit(1)

def install_firmware(firmware_file):
    print("  ⌛ Iniciando a instalação do Firmware...")
    print("-------------------------------------------------------------------------------")
    time.sleep(1)
    
    port = find_serial_port()
    if port:
        try:
            esptool.main(["--chip", "esp32", "--port", port, "--baud", "460800", "write_flash", "-z", "0x1000", firmware_file])
            print(FOOTER_TEXT)
        except Exception as e:
            print(f"Erro ao instalar o firmware no ESP32: {e}")
            sys.exit(1)
    else:
        print("Erro ao encontrar a porta serial do ESP32.")
        sys.exit(1)
