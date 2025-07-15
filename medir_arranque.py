import psutil
import subprocess
import time
import json
from web3 import Web3

# Configuración
PROCESO = "firefox"
NODO_IPS = ["192.168.20.34", "192.168.20.36", "192.168.20.37"]
PUERTOS = [8545, 8546, 8547]

CUENTA = "0x23fc7Ab0ad8bF6D6411a694e44A4034629175345"
PRIVATE_KEY = "0x5536524e82e93174c007a65d939e6891cb2ca7314cc52bdce2cd4713472dfd47"


# Paso 1: Medir tiempo de arranque real
def medir_tiempo_arranque(proceso):
    print(f"⏳ Lanzando '{proceso}' para medir tiempo de arranque...")

    t_inicio = time.time()
    subprocess.Popen([proceso], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    while True:
        time.sleep(0.1)
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proceso.lower() in proc.info['name'].lower():
                t_fin = time.time()
                return round(t_fin - t_inicio, 4)

# Paso 2: Registrar en blockchain como transacción
def registrar_tiempo_en_nodos(tiempo_arranque, proceso):
    mensaje = f"[PERFORMANCE] {proceso} promedio de arranque: {tiempo_arranque:.4f}s"

    for ip, puerto in zip(NODO_IPS, PUERTOS):
        web3 = Web3(Web3.HTTPProvider(f"http://{ip}:{puerto}"))
        if not web3.is_connected():
            print(f"❌ No se pudo conectar al nodo {ip}:{puerto}")
            continue

        nonce = web3.eth.get_transaction_count(CUENTA)
        base_fee = web3.eth.get_block("latest").baseFeePerGas
        max_fee = base_fee + web3.to_wei(2, 'gwei')
        priority_fee = web3.to_wei(1, 'gwei')

        tx = {
            'chainId': 1337,
            'nonce': nonce,
            'to': CUENTA,
            'value': 0,
            'gas': 50000,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': priority_fee,
            'data': web3.to_hex(text=mensaje)
        }

        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✅ Tiempo registrado en nodo {ip}:{puerto} con hash: {tx_hash.hex()}")

# Paso 3: Cargar historial y calcular promedio acumulado
def actualizar_promedio_y_guardar(nuevo_valor, archivo="historial_tiempos.json"):
    try:
        with open(archivo, 'r') as f:
            datos = json.load(f)
    except FileNotFoundError:
        datos = []

    datos.append(nuevo_valor)
    with open(archivo, 'w') as f:
        json.dump(datos, f)

    promedio = sum(datos) / len(datos)
    return round(promedio, 4)

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    tiempo = medir_tiempo_arranque(PROCESO)
    print(f"⏱ Tiempo de arranque medido: {tiempo:.4f} segundos")

    promedio = actualizar_promedio_y_guardar(tiempo)
    print(f"📊 Promedio histórico actualizado: {promedio:.4f} segundos")

    registrar_tiempo_en_nodos(promedio, PROCESO)
