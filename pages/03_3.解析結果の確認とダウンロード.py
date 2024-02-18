import os
import glob
import shutil
import base64
import json
from fractions import Fraction

import streamlit as st
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns

from const import RESULTS_DIR


def main():
    # 結果の確認とダウンロード
    st.markdown("## 3. 解析結果の確認とダウンロード")

    list_results = glob.glob(RESULTS_DIR + "*")
    list_results = [r[len(RESULTS_DIR):] for r in list_results]

    target_result = st.selectbox(
        "確認する結果",
        list_results,
        index=None, placeholder="ファイル名を選択してください")

    # 再生
    play_result_button = st.button("動画を再生する")
    if play_result_button:
        if not target_result:
            st.warning("確認する結果を選択してください。")
        else:
            with open(RESULTS_DIR + target_result + "/result.mp4", "rb") as f:
                st.video(f, format="video/mp4", start_time=0)

    # ダウンロード
    download_result_button = st.button("ダウンロードする")
    if download_result_button:
        if not target_result:
            st.warning("確認する結果を選択してください。")
        else:
            st.write("ダウンロードリンクを作成中です...")
            download_link = _create_download_zip(
                RESULTS_DIR + target_result, target_result + ".zip")
            st.markdown(download_link, unsafe_allow_html=True)

    # 表・グラフの可視化
    plot_button = st.button("表・グラフで可視化する")
    if plot_button:
        if not target_result:
            st.warning("確認する結果を選択してください。")
        else:
            dict_data = _read_data(
                RESULTS_DIR + target_result + "/result.json")
            width, height, wnorm, hnorm = _get_video_shape(
                RESULTS_DIR + target_result + "/result.mp4")
            list_target = ["親指", "人差し指", "中指", "薬指", "小指"]
            for target, tab in zip(list_target, st.tabs(list_target)):
                with tab:
                    list_which_hand = ["右手", "左手"]
                    dict_df = {
                        which: pd.DataFrame(dict_data[which][target], columns=["x座標", "y座標"])
                        for which in list_which_hand
                    }
                    with st.expander("要約統計量"):
                        for which, col in zip(list_which_hand,
                                              st.columns(len(list_which_hand))):
                            with col:
                                st.write(which)
                                df = dict_df[which]
                                st.dataframe(df.describe())
                    with st.expander("軌跡"):
                        for which, col in zip(list_which_hand,
                                              st.columns(len(list_which_hand))):
                            with col:
                                st.write(which)
                                df = dict_df[which]
                                plt.plot(df["x座標"], df["y座標"], marker="o")
                                plt.xlim(0, width)
                                plt.ylim(height, 0)
                                plt.xlabel("x座標", fontsize=20)
                                plt.ylabel("y座標", fontsize=20)
                                plt.tick_params(labelsize=18)
                                st.pyplot(plt)
                                plt.clf()
                    with st.expander("密度分布"):
                        for which, col in zip(list_which_hand,
                                              st.columns(len(list_which_hand))):
                            with col:
                                st.write(which)
                                df = dict_df[which]
                                plot = sns.jointplot(x="x座標", y="y座標", kind="kde", color="C3", data=df, fill=True)
                                plt.xlim(0, width)
                                plt.ylim(height, 0)
                                plt.xlabel("x座標", fontsize=20)
                                plt.ylabel("y座標", fontsize=20)
                                plt.tick_params(labelsize=18)
                                plot.fig.set_figwidth(wnorm)
                                plot.fig.set_figheight(hnorm)
                                st.pyplot(plot)
                                plt.clf()


def _create_download_zip(zip_directory, filename):
    """結果をzipにしてダウンロードリンクを返す関数

    streamlitのdownloadボタンは、あらかじめファイルをメモリにロードする必要があり、
    メモリを無駄に消費してしまう。

    この関数は、streamlitでなくHTMLでダウンロードするためのリンクを渡す関数

    Args:
        zip_directory (str):
            zipにしたいフォルダ名
        filename (str):
            ユーザーがダウンロードするときのファイル名

    Returns:
        str: HTMLのリンク
    """
    shutil.make_archive(zip_directory, 'zip', zip_directory)
    with open(zip_directory + ".zip", 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    href = f'<a href="data:file/zip;base64,{b64}" download=\'{filename}\'>\
            クリックしてダウンロードする \
        </a>'
    os.remove(zip_directory + ".zip")
    return href


def _read_data(filename):
    """結果JSONを読み込む関数

    Args:
        filename (str):
            結果ファイルのパス

    Returns:
        dict:
            結果JSON
    """
    # 指先のデータを取得する
    dict_data = {
        "右手": {
            "親指": [],
            "人差し指": [],
            "中指": [],
            "薬指": [],
            "小指": []
        },
        "左手": {
            "親指": [],
            "人差し指": [],
            "中指": [],
            "薬指": [],
            "小指": []
        }
    }
    en2jp = {
        "Right": "右手",
        "Left": "左手",
        "THUMB_TIP": "親指",
        "INDEX_FINGER_TIP": "人差し指",
        "MIDDLE_FINGER_TIP": "中指",
        "RING_FINGER_TIP": "薬指",
        "PINKY_TIP": "小指"
    }

    with open(filename) as f:
        list_results = json.load(f)
    for results in list_results:
        for result in results["Results"]:
            cateory_name = result["CategoryName"]
            for key in ["THUMB_TIP",
                        "INDEX_FINGER_TIP",
                        "MIDDLE_FINGER_TIP",
                        "RING_FINGER_TIP",
                        "PINKY_TIP"]:
                xy = result["Coordinates"][key]
                dict_data[en2jp[cateory_name]][en2jp[key]].append(xy)

    return dict_data


def _get_video_shape(filename):
    """動画ファイルの解像度を取得する関数

    Args:
        filename (str):
            動画ファイルのパス

    Returns:
        int: 幅
        int: 高さ
        int: 幅の比
        int: 高さの比
    """
    cap = cv2.VideoCapture(filename)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    tmp = Fraction(width, height)

    return width, height, tmp.numerator, tmp.denominator


if __name__ == "__main__":
    main()
