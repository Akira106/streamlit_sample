import os
import glob
import threading
import json

import cv2
import streamlit as st

import hands_detector
import video_writer
from const import UPLOAD_DIR, RESULTS_DIR


# 解析結果の保存先
if os.path.exists(RESULTS_DIR) is False:
    os.mkdir(RESULTS_DIR)


class AiModel():
    """AIモデルのクラス

    この例では手のひら検知を行う
    """
    def __init__(self):
        """コンストラクタ
        """
        # 手のひら検知
        self.detector = hands_detector.HandsDetector()
        # ユーザー間の排他ロック
        self.lock = threading.Lock()

    def try_lock(self):
        """ロック獲得関数

        Args:
            なし

        Returns:
            bool: 獲得成功 or 失敗
        """
        ret = self.lock.acquire(timeout=0)
        return ret

    def unlock(self):
        """ロック解放関数

        Args:
            なし

        Returns:
            なし

        Raises:
            獲得していないのに解放しようとするとエラーになる
        """
        self.lock.release()

    def detect(self, image_rgb):
        """検出関数

        Args:
            image_rgb (ndarray((height, width, 3), dtype=np.uint8)):
                RGR画像

        Returns:
            list(dict): 検出結果,
            ndarray((height, width, 3), dtype=np.uint8): 描画画像(RGB)
        """
        return self.detector.detect(image_rgb)


# st.cache_resourceの戻り値はユーザー間で共有される
# => AIオブジェクトは全ユーザーで共有される
@st.cache_resource
def load_model():
    AI = AiModel()
    return AI


def main():
    # AIモデル(全ユーザーで共有)
    AI = load_model()

    # 動画の選択
    st.markdown("## 2. 解析の実行")
    list_videos = glob.glob(UPLOAD_DIR + "*")
    list_videos = [v[len(UPLOAD_DIR):] for v in list_videos]
    target_video = st.selectbox(
        "解析する動画",
        list_videos,
        index=None, placeholder="動画を選択してください")
    play_button = st.button("選択した動画を再生する")
    if play_button:
        if not target_video:
            st.warning("解析する動画ファイルを選択してください。")
        else:
            # 選択した動画の再生
            with open(UPLOAD_DIR + target_video, "rb") as f:
                st.video(f, format="video/mp4", start_time=0)

    # 解析
    st.divider()  # 下に線を引く
    analyze_button = st.button("解析実行！！")
    if analyze_button:
        # 動画ファイルの選択チェック
        if not target_video:
            st.warning("解析する動画ファイルを選択してください。")
        else:
            cap = cv2.VideoCapture(UPLOAD_DIR + target_video)
            lock_ok = AI.try_lock()
            try:
                # 動画ファイルのチェック
                ret, emsg = _validate_video(cap)
                if ret is False:
                    st.warning(emsg)
                elif lock_ok is False:
                    st.warning("他のユーザーが使用中です。しばらくお待ちください")
                else:
                    # 解析開始
                    name = target_video.rsplit(".", maxsplit=1)[0]
                    outdir = RESULTS_DIR + name
                    if os.path.exists(outdir) is False:
                        os.mkdir(outdir)
                    nframe, shape, fps = _get_video_info(cap)
                    writer = video_writer.VideoWriter(
                        outdir + "/result.mp4", "h264", fps, shape)
                    list_results = []
                    progress = st.progress(0, text="解析中 ...")
                    for iframe in range(nframe):  # 解析ループ
                        ret, image = cap.read()
                        if ret is False:
                            # 解析終了
                            break
                        # 解析実行
                        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        results, drawn_image = AI.detect(image_rgb)
                        list_results.append({
                            "FrameNumber": iframe,
                            "Results": results
                        })
                        writer.write(drawn_image)
                        # 進捗バーの更新
                        percent = iframe / nframe
                        progress.progress(percent, text="解析中...")

                    # 終了処理
                    writer.release()
                    with open(outdir + "/result.json", "w") as f:
                        json.dump(list_results, f)
                    progress.progress(1.0, text="解析完了")
                    st.success("解析が完了しました。")

            finally:
                cap.release()
                if lock_ok is True:
                    AI.unlock()


def _validate_video(cap):
    """動画ファイルのチェック

    Args:
        cap (cv2.VideoCapture):
            ビデオキャプチャーオブジェクト

    Returns:
        bool:
            チェックの結果
        str or None:
            エラーメッセージ
    """
    emsg = \
        "動画ファイルの読み込みに失敗しました。  \n" + \
        "ファイル形式がサポートされていないか、ファイル拡張子が正しくないか、" + \
        "ファイルが破損している可能性があります。"
    if cap.isOpened() is False:
        return False, emsg

    nframe = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if nframe <= 0:
        return False, emsg

    return True, None


def _get_video_info(cap):
    """動画情報の取得

    Args:
        cap (cv2.VideoCapture):
            ビデオキャプチャーオブジェクト

    Returns:
        int: フレーム数
        tuple(int. int): 幅,高さ
        float: フレームレート
    """
    nframe = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    return nframe, (width, height), fps


if __name__ == "__main__":
    main()
