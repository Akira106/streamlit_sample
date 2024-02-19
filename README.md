# streamlitのサンプルプログラム

PythonのOSSであるstreamlitを使用したサンプルプログラムを作成しました。  
  
streamlitの公式ページ  
[https://streamlit.io/][https://streamlit.io/]  

## streamlitとは？

PythonだけでWebアプリを開発できるフレームワークです。  

- HTML、CSS、JavaScriptは不要です。
- フロントエンド、バックエンド、Webサーバーの実装を、Pythonだけでシームレスに記述することができます。
- Pythonの強力な機械学習ライブラリを簡単にWebアプリにできます。pandasやmatplotlibなどの可視化ツールともシームレスに連携することができます。

## このサンプルプログラムについて

このサンプルプログラムでは、以下のステップによるAI解析デモを実行します。  

- 1. 動画ファイルのアップロード
- 2. AI(手のひら検知)による解析の実行
- 3. 解析結果の確認・可視化とダウンロード

<br>

  Dockerとdocker-composeを使って、以下の手順により実行可能です。  

### 1. アプリのインストール

```shell-session
$ docker-compose build
```

### 2. アプリの起動

```shell-session
$ docker-compose up -d
```

→ `http://{サーバーのIPアドレス}:8080`にアクセスしてください。

### 3. アプリの終了

```shell-session
$ docker-compose down
```
