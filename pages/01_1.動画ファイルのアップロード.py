import os

import streamlit as st

from const import UPLOAD_DIR


# 動画のアップロード先
if os.path.exists(UPLOAD_DIR) is False:
    os.mkdir(UPLOAD_DIR)


def main():
    # 動画のアップロード
    st.markdown("## 1. 動画ファイルのアップロード")
    uploaded_file = st.file_uploader(
        "アップロードする動画ファイル(MP4)を選択してください。",
        type=["mp4"])

    if uploaded_file is not None:
        # ファイルの保存
        name = uploaded_file.name
        dst = UPLOAD_DIR + name
        with open(dst, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        st.success("「%s」のアップロードに成功しました。" % name)


if __name__ == "__main__":
    main()
