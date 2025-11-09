# marubiya Web Application

動的なウェブアプリケーションとして再構築された「お食事処 丸美屋」のサイトです。トップページとギャラリーページに加え、CMSライクな管理画面を備えており、文章や画像を管理者が更新できます。

## 必要環境

- Python 3.10 以上
- pip

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate  # Windows の場合は .venv\Scripts\activate
pip install -r requirements.txt
```

## 開発サーバーの起動

```bash
flask --app app run --debug
```

または Python から直接起動することもできます。

```bash
python app.py
```

初回起動時に SQLite データベース (`site.db`) が生成され、必要な初期データが投入されます。

## 管理画面

- URL: `http://localhost:5000/admin`
- 初期ユーザー: `admin`
- 初期パスワード: `admin123`

初回ログイン後、管理画面下部の「パスワード変更」から必ずパスワードを変更してください。環境変数 `MARUBIYA_INITIAL_PASSWORD` を設定すると、初期パスワードを任意の値に変更できます。また `MARUBIYA_SECRET_KEY` を設定すると Flask のシークレットキーを上書きできます。

## 主な機能

- サイト内文章の編集（トップページ、ギャラリーページ）
- トップページのヒーロー画像のアップロード／差し替え
- ギャラリー画像のアップロード・削除
- 管理者パスワードの変更

アップロードされた画像は `static/images/uploads/` に保存されます。既存の画像を差し替えた場合、古い画像は自動的に削除されます（初期画像を除く）。

## フロントエンド

- 既存のデザインを元にしたレスポンシブ対応のテンプレート
- 軽微なアニメーションを含む JavaScript (`static/js/main.js`)

## ライセンス

このプロジェクトは依頼元のためのサンプル実装です。用途に合わせて自由に拡張してください。
