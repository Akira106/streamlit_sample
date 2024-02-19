import streamlit as st


def main():
    # ページの設定
    st.set_page_config(
        page_title="streamlitのサンプルプログラム",  # タイトル
        page_icon=":smile:",  # ファビコン
        layout="wide",  # ページレイアウト
    )

    # 結果の確認とダウンロード
    st.header("streamlitのサンプルプログラム")
    st.markdown(
        "これはstreamlitのサンプルプログラムです。  \n" +
        "このサンプルプログラムでは、以下のステップによるAI解析デモを実行します。\n    ")
    st.markdown(
        "1. 動画ファイルのアップロード  \n" +
        "2. AI(手のひら検知)による解析の実行  \n" +
        "3. 解析結果の確認とダウンロード  "
    )

    st.markdown("### 左のサイドメニューをクリックして、各ステップを実行してください。")


if __name__ == "__main__":
    main()
