from web3 import Web3

# Lista de nodos
nodos = [
    ("192.168.20.34", 8545),
    ("192.168.20.36", 8546),
    ("192.168.20.37", 8547)
]

# Número de bloques recientes a inspeccionar por nodo
BLOQUES_A_REVISAR = 10

def inspeccionar_nodo(ip, puerto):
    print(f"\n🔍 Inspeccionando nodo {ip}:{puerto}")
    web3 = Web3(Web3.HTTPProvider(f"http://{ip}:{puerto}"))

    if not web3.is_connected():
        print("❌ No se pudo conectar.")
        return

    ultimo_bloque = web3.eth.block_number
    print(f"Último bloque: {ultimo_bloque}")

    for i in range(max(0, ultimo_bloque - BLOQUES_A_REVISAR + 1), ultimo_bloque + 1):
        bloque = web3.eth.get_block(i, full_transactions=True)
        print(f"\n🧱 Bloque #{i} - {len(bloque.transactions)} transacciones")

        for tx in bloque.transactions:
            try:
                entrada = tx.input
                if entrada and entrada != '0x':
                    log = web3.to_text(hexstr=entrada.hex())
                    print(f"📄 Log recuperado: {log}")
            except Exception as e:
                print(f"⚠️ Error al decodificar: {e}")

# Ejecutar para todos los nodos
for ip, puerto in nodos:
    inspeccionar_nodo(ip, puerto)
