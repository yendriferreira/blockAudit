# BlockAuditOS – Guía rápida de instalación y ejecución

Este **README** contiene el _paso a paso exacto_ para desplegar el prototipo **BlockAuditOS** en **tres** máquinas Ubuntu (físicas o virtuales) conectadas en red *bridge*.  
> Utilice `sudo` cuando su usuario no disponga de permisos de administrador.  
> Sustituya IP, puerto y `NODE_ID` según la VM.

---

## 1. Instalar dependencias básicas

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Paquetes imprescindibles
sudo apt install -y docker.io python3-venv git openssh-server jq curl xxd

# Habilitar servicios
sudo systemctl enable --now docker ssh
2. Clonar el repositorio y crear entorno Python
bash
Copiar
Editar
git clone https://github.com/<TU-USUARIO>/BlockAuditOS.git
cd BlockAuditOS

# Entorno virtual
python3 -m venv venv
source venv/bin/activate

# Librerías del proyecto
pip install --upgrade pip
pip install psutil==5.9.8 web3==7.12.0
3. Desplegar un nodo Ganache (en Docker)
VM-1 → NODE_ID=1 PORT=8545
VM-2 → NODE_ID=2 PORT=8546
VM-3 → NODE_ID=3 PORT=8547

bash
Copiar
Editar
NODE_ID=1          # 1, 2, 3 …
PORT=8545          # 8545, 8546, 8547 …

docker run -d --name ganache$NODE_ID \
  -v ~/ganache-data-node$NODE_ID:/data \
  -p $PORT:8545 \
  trufflesuite/ganache-cli:latest \
  --db /data --networkId 5777 \
  --mnemonic "audit audit audit audit audit audit audit audit audit audit audit audit" \
  --accounts 3 --defaultBalanceEther 1000
Verificar que el servicio RPC está escuchando:

bash
Copiar
Editar
ss -ltnp | grep $PORT
docker logs --tail 3 ganache$NODE_ID
4. Exportar la clave privada
Copie la private key de la primera cuenta que imprime Ganache y expórtela:

bash
Copiar
Editar
export PRIVATE_KEY=0x<CLAVE-HEX>
echo "export PRIVATE_KEY=$PRIVATE_KEY" >> ~/.bashrc
Recargue la sesión o ejecute source ~/.bashrc.

5. Configurar IPs de los nodos
Edite monitor_blockaudit.py dentro del repo:

python
Copiar
Editar
NODOS = [
    ("192.168.20.34", 8545),   # VM-1
    ("192.168.20.36", 8546),   # VM-2
    ("192.168.20.37", 8547)    # VM-3
]
6. Lanzar el monitor
bash
Copiar
Editar
source ~/BlockAuditOS/venv/bin/activate
cd ~/BlockAuditOS
python monitor_blockaudit.py
Debería ver en pantalla eventos JSON similares a:

json
Copiar
Editar
{"pid":2345,"name":"bash","status":"running","timestamp":"2025-07-15T11:57:08.914098"}
7. (Opcional) Generar carga de procesos
bash
Copiar
Editar
stress-ng --fork 100 --timeout 60s
El monitor registrará las creaciones y finalizaciones de esos procesos.

8. Verificar la cadena
Altura de bloque
bash
Copiar
Editar
curl -s -X POST http://192.168.20.34:8545 \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' | jq .
Los tres nodos deben devolver la misma altura (por ejemplo 0x1b8).

Hash de un bloque concreto
bash
Copiar
Editar
curl -s -X POST http://192.168.20.34:8545 \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["0x1b8",false],"id":1}' |
  jq .result.hash
Repita la consulta en los otros nodos; el hash debe coincidir.

Decodificar una transacción
bash
Copiar
Editar
TX_HASH=0x<hash>
curl -s -X POST http://192.168.20.34:8545 \
  -d '{"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":["'"$TX_HASH"'"],"id":1}' |
  jq -r .result.input | xxd -r -p
