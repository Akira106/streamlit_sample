import av


class VideoWriter():
    """動画作成クラス
    """
    def __init__(self, filename, codec, fps, shape, bit_rate=5000000):
        """コンストラクタ

        Args:
            filename (str): 動画ファイル名
            codec (str): コーデック (h264 or hevc)
            fps (float): フレームレート
            shape (tuple(int, int)): (幅, 高さ)
            bit_rate (int): ビットレート
        """
        self.writer = av.open(filename, "w")
        self.stream = self.writer.add_stream(codec, str(fps))
        self.stream.bit_rate = bit_rate
        self.stream.pix_fmt = "yuv420p"
        self.stream.width = shape[0]
        self.stream.height = shape[1]

    def write(self, image_rgb):
        """書き込み関数

        Args:
            image_rgb (ndarray((height, width, 3), dtype=np.uint8)):
                画像オブジェクト(RGB)

        Returns:
            なし
        """
        frame = av.VideoFrame.from_ndarray(image_rgb, format='rgb24')
        packet = self.stream.encode(frame)
        self.writer.mux(packet)

    def release(self):
        """書き込み終了
        """
        if self.writer is not None:
            # flush
            packet = self.stream.encode(None)
            self.writer.mux(packet)
            # close
            self.writer.close()
            self.writer = None

    def __del__(self):
        self.release()
