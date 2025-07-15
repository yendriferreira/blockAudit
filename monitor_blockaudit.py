import psutil
from datetime import datetime
import json
from web3 import Web3
from eth_account import Account

nodos = [
    ("192.168.20.34", 8545),
    ("192.168.20.36", 8546),
    ("192.168.20.37", 8547)
]

cuenta = "0x23fc7Ab0ad8bF6D6411a694e44A4034629175345"
private_key = "0x5536524e82e93174c007a65d939e6891cb2ca7314cc52bdce2cd4713472dfd47"

def capturar_eventos(limit=5):
    eventos = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
        try:
            info = proc.info
            info["timestamp"] = datetime.now().isoformat()
            eventos.append(info)
        except Exception:
            pass
    return eventos[:limit]
# evento = {
#     'proceso': 'firefox',
#     'pid': 12345,
#     'usuario': 'vboxuser'
# }

def registrar_evento(ip, puerto, evento):
    url = f"http://{ip}:{puerto}"
    web3 = Web3(Web3.HTTPProvider(url))

    if web3.is_connected():
        print(f"[OK] Conectado a nodo {ip}:{puerto}")

        # MUY IMPORTANTE: el nonce lo calculamos dentro de cada nodo
        nonce = web3.eth.get_transaction_count(cuenta)

        tx = {
            'nonce': nonce,
            'to': cuenta,
            'value': 0,
            'gas': 50000,
            'maxFeePerGas': web3.to_wei('1', 'gwei'),
            'maxPriorityFeePerGas': web3.to_wei('1', 'gwei'),
            'data': web3.to_hex(text=str(evento)),
            'chainId': web3.eth.chain_id
        }

        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"Evento registrado en bloque con hash: {tx_hash.hex()}")

    else:
        print(f"[ERROR] No se pudo conectar a nodo {ip}:{puerto}")

# for ip, puerto in nodos:
#     registrar_evento(ip, puerto, evento)
for evento in capturar_eventos():
    for ip, puerto in nodos:
        registrar_evento(ip, puerto, evento)


