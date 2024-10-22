import cv2
import mediapipe as mp
import serial


arduino = serial.Serial('COM5', 9600)
video = cv2.VideoCapture(0)

hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=2)
mpraw = mp.solutions.drawing_utils

previous_finger_states_right = [False, False, False, False, False]
previous_finger_states_left = [False, False, False, False, False]

cv2.namedWindow("video", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    check, img = video.read()

    if not check:
        print("Erro ao capturar imagem")
        break

    img = cv2.flip(img, 1)

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = Hand.process(imgRGB)
    h, w, _ = img.shape

    texto = "PIANO VIRTUAL UEPA"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mpraw.draw_landmarks(img, hand_landmarks, hand.HAND_CONNECTIONS)

            for cord in hand_landmarks.landmark:
                cx, cy = int(cord.x * w), int(cord.y * h)
                cv2.circle(img, (cx, cy), 5, (255, 0, 0), -1)  # Cor azul (BGR)

            dedos = [8, 12, 16, 20]
            dedos_esquerda = [8, 12, 16, 20]

            if hand_landmarks.landmark[5].x > hand_landmarks.landmark[0].x: 
                finger_states_right = []

                if hand_landmarks.landmark[4].x < hand_landmarks.landmark[2].x:  
                    finger_states_right.append(True)  
                else:
                    finger_states_right.append(False)  

                for x in dedos:
                    if hand_landmarks.landmark[x].y > hand_landmarks.landmark[x - 2].y: 
                        finger_states_right.append(True)
                    else:
                        finger_states_right.append(False)

                for i in range(5):
                    if finger_states_right[i] != previous_finger_states_right[i]:
                        if finger_states_right[i]:
                            if i == 0:
                                arduino.write(b'G')
                                print("SOL (esq)")
                            elif i == 1:
                                arduino.write(b'F')
                                print("FA (esq)")
                            elif i == 2:
                                arduino.write(b'E')
                                print("MI (esq)")
                            elif i == 3:
                                arduino.write(b'D')
                                print("FA (esq)")
                            elif i == 4:
                                arduino.write(b'C')
                                print("DO (esq)")
                        else:
                            arduino.write(b'S')
                            print("Nenhuma nota (esq)")

                previous_finger_states_right = finger_states_right

            elif hand_landmarks.landmark[5].x < hand_landmarks.landmark[0].x:  
                finger_states_left = []

                if hand_landmarks.landmark[4].x > hand_landmarks.landmark[2].x:  
                    finger_states_left.append(True)  
                else:
                    finger_states_left.append(False)  

                for x in dedos_esquerda:
                    if hand_landmarks.landmark[x].y > hand_landmarks.landmark[x - 2].y: 
                        finger_states_left.append(True)
                    else:
                        finger_states_left.append(False)

                for i in range(5):
                    if finger_states_left[i] != previous_finger_states_left[i]:
                        if finger_states_left[i]:
                            if i == 0:
                                arduino.write(b'A')
                                print("DO (dir)")
                            elif i == 1:
                                arduino.write(b'B')
                                print("RE (dir)")
                            elif i == 2:
                                arduino.write(b'C4')
                                print("DO2 (dir)")
                            elif i == 3:
                                arduino.write(b'D4')
                                print("RE2 (dir)")
                            elif i == 4:
                                arduino.write(b'E4')
                                print("MI2 (dir)")
                        else:
                            arduino.write(b'S')
                            print("Nenhuma nota (Direita)")

                previous_finger_states_left = finger_states_left

    else:
        arduino.write(b'S')
        print("Nenhuma mão na webcam")

    cv2.rectangle(img, (280, 10), (1000, 100), (255, 0, 0), -1)
    text_size = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    text_x = (img.shape[1] - text_size[0]) // 2
    text_y = (100 + text_size[1]) // 2  
    cv2.putText(img, texto, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    finger_messages = [
        "Polegar esquerda = DO",
        "Indicador esquerda = RE",
        "Medio esquerda = MI",
        "Anelar esquerda = FA",
        "Minimo esquerda = SOL",
        "Polegar direita = LA",
        "Indicador direita = SI",
    ]

    text_x_left = 10  
    text_y_left = h - 10 

    for message in finger_messages:
        text_size = cv2.getTextSize(message, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
        cv2.putText(img, message, (text_x_left, text_y_left), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        text_y_left -= text_size[1] + 5 

    info_text = "UEPA 2024"
    text_size = cv2.getTextSize(info_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    text_x_right = w - text_size[0] - 10  
    text_y_right = h - 10  

    cv2.putText(img, info_text, (text_x_right, text_y_right), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("video", img)

    key = cv2.waitKey(1)

    if key == 27:
        break

video.release()
cv2.destroyAllWindows()
arduino.close()
