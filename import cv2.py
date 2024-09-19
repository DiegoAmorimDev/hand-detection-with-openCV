import cv2
import mediapipe as mp
import serial

# Inicializa a captura de vídeo
video = cv2.VideoCapture(0)

# Inicializa a solução de mãos do Mediapipe
hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=1)
mpraw = mp.solutions.drawing_utils

# Configura a comunicação serial com o Arduino
arduino = serial.Serial('COM5', 9600)  # Substitua 'COM5' pela porta correta do seu Arduino

# Mapeamento dos dedos para notas
note_mapping = {
    0: 'C',  # Polegar
    1: 'D',  # Índice
    2: 'E',  # Médio
    3: 'F',  # Anelar
    4: 'G'   # Mínimo
}

def get_finger_state(hand_landmarks):
    """ Retorna quais dedos estão abaixados. """
    finger_states = {}
    if hand_landmarks:
        landmarks = hand_landmarks.landmark
        # Ajuste a lógica para verificar o estado dos dedos
        for i in range(5):  # Há 5 dedos
            # Checar se o dedo está abaixado comparando o y das landmarks
            # Use landmarks 0 e 2 para o polegar, 1 e 3 para o indicador, etc.
            # Exemplo para o polegar:
            if landmarks[hand.HAND_CONNECTIONS[i][0]].y > landmarks[hand.HAND_CONNECTIONS[i][1]].y:
                finger_states[i] = True
            else:
                finger_states[i] = False
    return finger_states

while True:
    # Captura o frame de vídeo
    check, img = video.read()
    if not check:
        print("Erro ao capturar imagem")
        break

    # Converte o frame para RGB
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Processa a imagem e detecta as mãos
    results = Hand.process(imgRGB)
    handsPoints = results.multi_hand_landmarks
    w, h, _ = img.shape

    # Se houver detecção de mão, desenha as landmarks na imagem original
    if handsPoints:
        for hand_landmarks in handsPoints:
            mpraw.draw_landmarks(img, hand_landmarks, hand.HAND_CONNECTIONS)
            finger_states = get_finger_state(hand_landmarks)

            # Envia a nota para o Arduino se o dedo estiver abaixado
            for finger, state in finger_states.items():
                if state:
                    note = note_mapping.get(finger, 'S')  # 'S' para parar o som se o dedo não estiver mapeado
                    arduino.write(note.encode())
                    print(f"Dedo {finger} abaixado - Nota {note}")
                else:
                    # Envia um sinal para parar o som
                    arduino.write(b'S')  # 'S' para parar o som
                    print(f"Dedo {finger} levantado")

    # Exibe o vídeo com as detecções
    cv2.imshow("video", img)

    # Captura a tecla pressionada
    key = cv2.waitKey(1)

    # Pressionar 'ESC' (código 27) para sair
    if key == 27:
        break

# Libera o recurso de captura de vídeo e fecha as janelas
video.release()
cv2.destroyAllWindows()


