import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2


MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


class HandsDetector():
    """手のひら検知
    """
    def __init__(self):
        """コンストラクタ
        """
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.list_label = [
            "WRIST",
            "THUMB_CMC",
            "THUMB_MCP",
            "THUMB_IP",
            "THUMB_TIP",
            "INDEX_FINGER_MCP",
            "INDEX_FINGER_PIP",
            "INDEX_FINGER_DIP",
            "INDEX_FINGER_TIP",
            "MIDDLE_FINGER_MCP",
            "MIDDLE_FINGER_PIP",
            "MIDDLE_FINGER_DIP",
            "MIDDLE_FINGER_TIP",
            "RING_FINGER_MCP",
            "RING_FINGER_PIP",
            "RING_FINGER_DIP",
            "RING_FINGER_TIP",
            "PINKY_MCP",
            "PINKY_PIP",
            "PINKY_DIP",
            "PINKY_TIP"
        ]

    def detect(self, image_rgb):
        """検出関数

        Args:
            image_bgr (ndarray((height, width, 3), dtype=np.uint8)):
                RGB画像

        Returns:
            list(dict): 検出結果,
            ndarray((height, width, 3), dtype=np.uint8): 描画画像(RGB)
        """
        image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb)
        detection_result = self.detector.detect(image)
        return self._to_json(image_rgb, detection_result), self._draw(image_rgb, detection_result)

    def _to_json(self, image_rgb, detection_result):
        """JSON変換関数
        mediapipe独自のオブジェクトをJSONフォーマットに変換する

        Args:
            image (ndarray((height, width, 3), dtype=np.uint8)):
                画像オブジェクト
            detedetection_result (mediapipe.tasks.python.vision.hand_landmarker.HandLandmarkerResult):
                解析結果

        Returns:
            list(dict):
                JSONフォーマット
        """
        h, w = image_rgb.shape[:2]
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness

        # Loop through the detected hands
        result_json = []
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx]
            result_dict = {}

            result_dict["CategoryName"] = handedness[0].category_name
            result_dict["Score"] = handedness[0].score
            coordinates = np.array([[landmark.x, landmark.y] for landmark in hand_landmarks])
            coordinates[:, 0] *= w
            coordinates[:, 1] *= h
            result_dict["Coordinates"] = {self.list_label[i]: coord for i, coord in enumerate(coordinates.tolist())}

            result_json.append(result_dict)
        return result_json

    def _draw(self, image_rgb, detection_result):
        """描画関数

        Args:
            image_rgb (ndarray((height, width, 3), dtype=np.uint8)):
                画像オブジェクト(RGB)
            detedetection_result (mediapipe.tasks.python.vision.hand_landmarker.HandLandmarkerResult):
                解析結果

        Returns:
            ndarray((height, width, 3), dtype=np.uint8):
                RGB画像
        """
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = np.copy(image_rgb)

        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx]

            # Draw the hand landmarks.
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
              landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])
            solutions.drawing_utils.draw_landmarks(
              annotated_image,
              hand_landmarks_proto,
              solutions.hands.HAND_CONNECTIONS,
              solutions.drawing_styles.get_default_hand_landmarks_style(),
              solutions.drawing_styles.get_default_hand_connections_style())

            # Get the top left corner of the detected hand's bounding box.
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - MARGIN

            # Draw handedness (left or right hand) on the image.
            cv2.putText(annotated_image, f"{handedness[0].category_name}",
                        (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                        FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

        return annotated_image
