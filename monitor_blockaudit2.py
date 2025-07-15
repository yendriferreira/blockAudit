import psutil
from datetime import datetime
from web3 import Web3
from eth_account import Account
import time

# Información de cuenta (ajusta con tu cuenta de Ganache)
cuenta = "0x23fc7Ab0ad8bF6D6411a694e44A4034629175345"
private_key = "0x5536524e82e93174c007a65d939e6891cb2ca7314cc52bdce2cd4713472dfd47"

# Lista de nodos blockchain
nodos = [
    ("192.168.20.34", 8545),
    ("192.168.20.36", 8546),
    ("192.168.20.37", 8547)
]

# Configuración de Web3 por nodo
web3s = []
for ip, puerto in nodos:
    url = f"http://{ip}:{puerto}"
    web3 = Web3(Web3.HTTPProvider(url))
    web3s.append((web3, ip, puerto))


# Obtener snapshot de procesos
def snapshot():
    return {p.pid: p.info for p in psutil.process_iter(['pid', 'name', 'username', 'status'])}


# Función para enviar el evento como transacción
def registrar_evento(web3, evento):
    try:
        nonce = web3.eth.get_transaction_count(cuenta)
        base_fee = web3.eth.get_block("latest").baseFeePerGas
        max_fee = base_fee + web3.to_wei('2', 'gwei')
        tx = {
            'nonce': nonce,
            'to': cuenta,
            'value': 0,
            'data': web3.to_hex(text=str(evento)),
            'gas': 50000,
            'maxFeePerGas': max_fee,
            'maxPriorityFeePerGas': web3.to_wei('1', 'gwei'),
            'chainId': web3.eth.chain_id
        }
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"🟢 Evento registrado en bloque con hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"❌ Error al registrar evento: {e}")


# Bucle principal
print("🟡 Iniciando monitoreo del sistema... (Ctrl+C para detener)")
old_snapshot = snapshot()

try:
    while True:
        time.sleep(2)
        new_snapshot = snapshot()

        # Detectar procesos nuevos
        nuevos_pids = set(new_snapshot.keys()) - set(old_snapshot.keys())
        for pid in nuevos_pids:
            evento = new_snapshot[pid]
            evento['timestamp'] = datetime.now().isoformat()

            print(f"🕵️‍♂️ Nuevo proceso detectado: {evento}")

            # Registrar en todos los nodos
            for web3, ip, puerto in web3s:
                if web3.is_connected():
                    print(f"[OK] Conectado a nodo {ip}:{puerto}")
                    registrar_evento(web3, evento)
                else:
                    print(f"[ERROR] No se pudo conectar a {ip}:{puerto}")

        old_snapshot = new_snapshot

except KeyboardInterrupt:
    print("\n🛑 Monitoreo detenido por el usuario.")
