import socket
import cv2
import numpy as np
import json
from ultralytics import YOLO

# Inicializa o modelo (isso demora alguns segundos, por isso fazemos FORA do loop)
model = YOLO('yolo11n.pt')
vehicle_classes = [2, 3, 5, 7]

# Configura o socket UDP para escutar na porta 9000
sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_servidor.bind(("0.0.0.0", 9000))

print("[*] Servidor Cloud de IA aguardando streams de vídeo...")

while True:
    # Recebe os bytes do JPEG. Usamos um buffer grande (65535)
    dados_bytes, endereco_cliente = sock_servidor.recvfrom(65535)

    # 1. Transformar os bytes recebidos de volta em um array do NumPy
    np_arr = np.frombuffer(dados_bytes, dtype=np.uint8)

    # 2. Decodificar o JPEG para uma matriz de imagem do OpenCV
    frame_recebido = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    frame_count = 0

    if frame_recebido is not None:
        frame_count += 1
        # 3. Roda a IA!
        results = model.predict(frame_recebido, conf=0.5, classes=vehicle_classes, verbose=False)

        # Extrai a quantidade de veículos detectados
        contagem = len(results[0].boxes)

        print(f"[+] Tamanho: {len(dados_bytes)} bytes | Veículos detectados: {contagem}")

        # Monta o dicionário e envia a resposta de volta ao cliente na porta 9001
        resposta = {"carros": contagem}
        dados_json = json.dumps(resposta).encode('utf-8')

        
        
        dest = (endereco_cliente[0], 9001)
        sock_servidor.sendto(dados_json, dest)