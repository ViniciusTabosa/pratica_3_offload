import cv2
import socket
import json

SERVER_IP = "127.0.0.1"
SERVER_PORT_VIDEO = 9000
SERVER_PORT_JSON = 9001 # O cliente vai escutar o retorno nesta porta


sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_recebimento.bind((SERVER_IP, SERVER_PORT_JSON))
sock_recebimento.settimeout(0.1)  # Define um tempo limite para receber dados
dados_json = None  # Inicializa a variável para armazenar os dados JSON recebidos

cap = cv2.VideoCapture("video.mp4")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # 1. Reduzir a resolução para caber no pacote UDP (ex: 320x240 ou 640x480)
    frame_redimensionado = cv2.resize(frame, (480, 320))

    # 2. Comprimir o frame para formato JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    result, encimg = cv2.imencode('.jpg', frame_redimensionado, encode_param)

    # 3. Converter para bytes puros
    dados_bytes = encimg.tobytes()

    # Verificação de segurança 65 kb
    if len(dados_bytes) < 65000:
        try:
            sock_envio.sendto(dados_bytes, (SERVER_IP, SERVER_PORT_VIDEO))
        except:
            pass
    else:
        print("Quadro grande demais para UDP!")


    # TODO: RECEBER O RETORNO DA NUVEM (JSON)
    try:
        msg, _ = sock_recebimento.recvfrom(1024)
        dados_json = json.loads(msg.decode('utf-8'))
    except socket.timeout:
        pass


    # TODO: MOSTRAR O RESULTADO NA TELA
    if dados_json is not None:
        # Obtém a quantidade de carros
        qtd_carros = dados_json.get('carros', 0)
        
        cv2.putText(
            frame_redimensionado,
            f"Carros: {qtd_carros}",
            (10, 30),                  
            cv2.FONT_HERSHEY_SIMPLEX,  
            0.8,                       
            (0, 255, 0),               
            2                          
        )

    cv2.imshow("Dashcam - Visão do Motorista", frame_redimensionado)
    if cv2.waitKey(30) & 0xFF == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()