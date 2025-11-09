import os
from datetime import datetime
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("MARUBIYA_SECRET_KEY", "change-me"),
    SQLALCHEMY_DATABASE_URI="sqlite:///site.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "images", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}


db = SQLAlchemy(app)


class AdminUser(db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class SiteContent(db.Model):
    __tablename__ = "site_content"

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=False)


class GalleryImage(db.Model):
    __tablename__ = "gallery_images"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


SITE_CONTENT_SCHEMA = [
    {
        "section": "サイト全体",
        "fields": [
            {
                "key": "site_brand",
                "label": "サイト名",
                "type": "text",
                "default": "お食事処 丸美屋",
            },
            {
                "key": "site_description",
                "label": "サイト説明 (meta description)",
                "type": "textarea",
                "default": "奈良・お食事処 丸美屋の公式サイト。旬の味わいと心づくしのおもてなしをご紹介します。",
            },
            {
                "key": "footer_contact",
                "label": "フッターの連絡先",
                "type": "textarea",
                "default": "お食事処 丸美屋｜〒630-8215 奈良県奈良市東向中町26｜TEL 0742-**-****",
            },
            {
                "key": "footer_notice",
                "label": "フッターのコピーライト表記",
                "type": "text",
                "default": "お食事処 丸美屋 All rights reserved.",
            },
        ],
    },
    {
        "section": "トップページ｜ヒーローエリア",
        "fields": [
            {
                "key": "hero_tag",
                "label": "ヒーロータグ",
                "type": "text",
                "default": "奈良・東向商店街",
            },
            {
                "key": "hero_title",
                "label": "メイン見出し",
                "type": "textarea",
                "default": "店頭の佇まいと旬の味わいを、そのままに。",
            },
            {
                "key": "hero_subtitle",
                "label": "サブコピー",
                "type": "textarea",
                "default": "木の香りがやさしく包む店内で、手づくりの定食と季節の小鉢をゆっくりとお楽しみください。",
            },
            {
                "key": "hero_info_label_1",
                "label": "情報1 ラベル",
                "type": "text",
                "default": "ランチ・ディナー",
            },
            {
                "key": "hero_info_value_1",
                "label": "情報1 内容",
                "type": "text",
                "default": "毎日手づくりの献立をご用意",
            },
            {
                "key": "hero_info_label_2",
                "label": "情報2 ラベル",
                "type": "text",
                "default": "近鉄奈良駅から徒歩3分",
            },
            {
                "key": "hero_info_value_2",
                "label": "情報2 内容",
                "type": "text",
                "default": "テイクアウトにも対応しています",
            },
            {
                "key": "hero_primary_button_text",
                "label": "ボタン1 テキスト",
                "type": "text",
                "default": "お席のご相談",
            },
            {
                "key": "hero_primary_button_link",
                "label": "ボタン1 リンク",
                "type": "text",
                "default": "#reservation",
            },
            {
                "key": "hero_secondary_button_text",
                "label": "ボタン2 テキスト",
                "type": "text",
                "default": "店内の雰囲気を見る",
            },
            {
                "key": "hero_secondary_button_link",
                "label": "ボタン2 リンク",
                "type": "text",
                "default": "gallery",
            },
            {
                "key": "hero_image_alt",
                "label": "ヒーロー画像の代替テキスト",
                "type": "text",
                "default": "丸美屋の店内イメージ",
            },
        ],
    },
    {
        "section": "トップページ｜丸美屋について",
        "fields": [
            {
                "key": "concept_title",
                "label": "セクション見出し",
                "type": "text",
                "default": "丸美屋について",
            },
            {
                "key": "concept_intro",
                "label": "紹介文",
                "type": "textarea",
                "default": "創業以来大切にしているのは、旬の食材を丁寧に仕込み、お客様一人ひとりに寄り添うこと。昼は定食や丼もの、夜はお酒とともに楽しめる一品料理をご用意しています。",
            },
            {
                "key": "concept_card_1_title",
                "label": "カード1 見出し",
                "type": "text",
                "default": "奈良の旬を味わう",
            },
            {
                "key": "concept_card_1_body",
                "label": "カード1 本文",
                "type": "textarea",
                "default": "大和肉鶏や旬の野菜など、地元の素材を活かした献立をご提供。季節替わりの小鉢や炊き込みご飯も好評です。",
            },
            {
                "key": "concept_card_2_title",
                "label": "カード2 見出し",
                "type": "text",
                "default": "くつろぎの空間",
            },
            {
                "key": "concept_card_2_body",
                "label": "カード2 本文",
                "type": "textarea",
                "default": "木の温かみを活かした落ち着いた店内。お一人さまからご家族までゆったりお過ごしいただけるお席をご用意しています。",
            },
            {
                "key": "concept_card_3_title",
                "label": "カード3 見出し",
                "type": "text",
                "default": "心づくしのおもてなし",
            },
            {
                "key": "concept_card_3_body",
                "label": "カード3 本文",
                "type": "textarea",
                "default": "スタッフが笑顔でお迎えし、ひと皿ひと皿に心を込めてお届けします。初めての方もお気軽にお立ち寄りください。",
            },
        ],
    },
    {
        "section": "トップページ｜季節のおしながき",
        "fields": [
            {
                "key": "seasonal_title",
                "label": "セクション見出し",
                "type": "text",
                "default": "季節のおしながき",
            },
            {
                "key": "seasonal_intro",
                "label": "紹介文",
                "type": "textarea",
                "default": "定番の定食に加え、季節の野菜や食材を使った限定メニューをご用意しています。詳しい内容は店頭とSNSで発信中です。",
            },
            {
                "key": "seasonal_card_1_title",
                "label": "カード1 見出し",
                "type": "text",
                "default": "昼のお食事",
            },
            {
                "key": "seasonal_card_1_body",
                "label": "カード1 本文",
                "type": "textarea",
                "default": "丸美屋定食・日替わり定食・かつ丼・天丼など、ボリュームたっぷりの献立をご用意。お持ち帰りにも対応しています。",
            },
            {
                "key": "seasonal_card_2_title",
                "label": "カード2 見出し",
                "type": "text",
                "default": "夜のお食事",
            },
            {
                "key": "seasonal_card_2_body",
                "label": "カード2 本文",
                "type": "textarea",
                "default": "季節の小鉢、だし巻き玉子、串カツなど、お酒と相性の良い一品料理が充実。ちょい飲みセットも人気です。",
            },
            {
                "key": "seasonal_card_3_title",
                "label": "カード3 見出し",
                "type": "text",
                "default": "甘味とおみやげ",
            },
            {
                "key": "seasonal_card_3_body",
                "label": "カード3 本文",
                "type": "textarea",
                "default": "食後の甘味やテイクアウト用のお惣菜もございます。旅のお土産やご家庭の食卓にもどうぞ。",
            },
        ],
    },
    {
        "section": "トップページ｜営業時間",
        "fields": [
            {
                "key": "hours_title",
                "label": "セクション見出し",
                "type": "text",
                "default": "営業時間・営業日",
            },
            {
                "key": "hours_intro",
                "label": "紹介文",
                "type": "textarea",
                "default": "ご来店の前にご確認ください。臨時休業・貸切などの情報は店頭掲示とお電話にてご案内いたします。",
            },
            {
                "key": "hours_lunch_label",
                "label": "ランチ ラベル",
                "type": "text",
                "default": "ランチ",
            },
            {
                "key": "hours_lunch_value",
                "label": "ランチ 内容",
                "type": "text",
                "default": "11:30〜14:30（L.O. 14:00）",
            },
            {
                "key": "hours_dinner_label",
                "label": "ディナー ラベル",
                "type": "text",
                "default": "ディナー",
            },
            {
                "key": "hours_dinner_value",
                "label": "ディナー 内容",
                "type": "text",
                "default": "17:00〜21:00（L.O. 20:30）",
            },
            {
                "key": "hours_closed_label",
                "label": "定休日 ラベル",
                "type": "text",
                "default": "日曜・第3月曜",
            },
            {
                "key": "hours_closed_value",
                "label": "定休日 補足",
                "type": "text",
                "default": "※祝日の場合は翌平日休",
            },
            {
                "key": "hours_notice",
                "label": "注意書き",
                "type": "textarea",
                "default": "※営業時間・定休日は取材時点の情報です。季節や仕入れ状況により変更となる場合がございますので、最新の営業状況はお電話でお問い合わせください。",
            },
        ],
    },
    {
        "section": "トップページ｜Instagram・ギャラリー",
        "fields": [
            {
                "key": "instagram_title",
                "label": "Instagram 見出し",
                "type": "text",
                "default": "Instagram",
            },
            {
                "key": "instagram_caption",
                "label": "Instagram 説明",
                "type": "textarea",
                "default": "最新情報はSNSでご紹介予定です。",
            },
            {
                "key": "instagram_button_label",
                "label": "Instagram ボタンの文言",
                "type": "text",
                "default": "Instagram準備中",
            },
            {
                "key": "instagram_button_url",
                "label": "Instagram ボタンのリンク",
                "type": "text",
                "default": "",
            },
            {
                "key": "instagram_button_enabled",
                "label": "Instagram ボタン有効化 (true/false)",
                "type": "text",
                "default": "false",
            },
            {
                "key": "gallery_link_label",
                "label": "ギャラリーリンク文言",
                "type": "text",
                "default": "店内写真ギャラリーを見る",
            },
        ],
    },
    {
        "section": "トップページ｜アクセス",
        "fields": [
            {
                "key": "access_title",
                "label": "セクション見出し",
                "type": "text",
                "default": "アクセス",
            },
            {
                "key": "access_intro",
                "label": "紹介文",
                "type": "textarea",
                "default": "近鉄奈良駅より徒歩数分。周辺にはコインパーキングもございます。ご不明な点はお気軽にお問い合わせください。",
            },
            {
                "key": "access_address_heading",
                "label": "所在地 見出し",
                "type": "text",
                "default": "所在地",
            },
            {
                "key": "access_address_body",
                "label": "所在地 内容",
                "type": "textarea",
                "default": "〒630-8215 奈良県奈良市東向中町26\n近鉄奈良駅（東改札）より徒歩3分、東向商店街沿い。",
            },
            {
                "key": "access_contact_heading",
                "label": "お問い合わせ 見出し",
                "type": "text",
                "default": "お問い合わせ",
            },
            {
                "key": "access_contact_phone",
                "label": "電話番号表示",
                "type": "textarea",
                "default": "TEL：0742-**-****\n※電話番号は更新時に差し替えてください。",
            },
            {
                "key": "access_contact_body",
                "label": "お問い合わせ本文",
                "type": "textarea",
                "default": "ご予約・団体利用のご相談はお電話にて承ります。",
            },
            {
                "key": "map_embed_url",
                "label": "Googleマップ埋め込みURL",
                "type": "text",
                "default": "https://maps.google.com/maps?q=%E5%A5%88%E8%89%AF%E7%9C%8C%E5%A5%88%E8%89%AF%E5%B8%82%E6%9D%B1%E5%90%91%E4%B8%AD%E7%94%BA26%20%E4%B8%B8%E7%BE%8E%E5%B1%8B&t=&z=17&ie=UTF8&iwloc=&output=embed",
            },
        ],
    },
    {
        "section": "ギャラリーページ",
        "fields": [
            {
                "key": "gallery_title",
                "label": "見出し",
                "type": "text",
                "default": "写真ギャラリー",
            },
            {
                "key": "gallery_intro",
                "label": "紹介文",
                "type": "textarea",
                "default": "店内の雰囲気やお料理の一例をご紹介します。実際の写真は撮影が整い次第随時更新いたします。",
            },
            {
                "key": "gallery_back_link_label",
                "label": "トップへ戻るリンク文言",
                "type": "text",
                "default": "← トップページに戻る",
            },
        ],
    },
]

HERO_IMAGE_KEY = "hero_image"
HERO_IMAGE_DEFAULT = "images/exterior.svg"


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage) -> str | None:
    if not file_storage or file_storage.filename == "":
        return None

    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    name, ext = os.path.splitext(filename)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    new_filename = f"{name}_{timestamp}{ext}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
    file_storage.save(file_path)
    relative_path = os.path.join("images", "uploads", new_filename)
    return relative_path.replace("\\", "/")


def get_site_content() -> dict[str, str]:
    content = {item.key: item.value for item in SiteContent.query.all()}
    for section in SITE_CONTENT_SCHEMA:
        for field in section["fields"]:
            content.setdefault(field["key"], field.get("default", ""))
    content.setdefault(HERO_IMAGE_KEY, HERO_IMAGE_DEFAULT)
    return content


def seed_defaults() -> None:
    for section in SITE_CONTENT_SCHEMA:
        for field in section["fields"]:
            if SiteContent.query.get(field["key"]) is None:
                db.session.add(SiteContent(key=field["key"], value=field.get("default", "")))
    if SiteContent.query.get(HERO_IMAGE_KEY) is None:
        db.session.add(SiteContent(key=HERO_IMAGE_KEY, value=HERO_IMAGE_DEFAULT))

    if AdminUser.query.filter_by(username="admin").first() is None:
        default_user = AdminUser(username="admin")
        default_user.set_password(os.environ.get("MARUBIYA_INITIAL_PASSWORD", "admin123"))
        db.session.add(default_user)

    if GalleryImage.query.count() == 0:
        defaults = [
            ("images/exterior.svg", "夕暮れ時の外観。暖簾をくぐると木の香り漂う店内へ。"),
            ("images/dining-room.svg", "カウンター席とテーブル席をご用意。お一人さまも居心地よくお過ごしいただけます。"),
            ("images/signature-dish.svg", "旬の食材を使ったお料理。彩り豊かな小鉢と一緒にどうぞ。"),
        ]
        for filename, caption in defaults:
            db.session.add(GalleryImage(filename=filename, caption=caption))

    db.session.commit()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("admin_user_id"):
            flash("ログインしてください。", "warning")
            return redirect(url_for("admin_login", next=request.path))
        return view(**kwargs)

    return wrapped_view


@app.context_processor
def inject_site_content():
    return {"site_content": get_site_content()}


@app.route("/")
def index():
    content = get_site_content()
    instagram_enabled = content.get("instagram_button_enabled", "false").lower() == "true"
    hero_image = content.get(HERO_IMAGE_KEY, HERO_IMAGE_DEFAULT)
    hero_image_url = None
    if hero_image:
        hero_image_url = url_for("static", filename=hero_image)
    return render_template(
        "index.html",
        instagram_enabled=instagram_enabled,
        hero_image_url=hero_image_url,
    )


@app.route("/gallery")
def gallery():
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template("gallery.html", gallery_images=images)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = AdminUser.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["admin_user_id"] = user.id
            flash("ログインしました。", "success")
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        flash("ログイン情報が正しくありません。", "danger")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_user_id", None)
    flash("ログアウトしました。", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    content = get_site_content()
    gallery_images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()

    if request.method == "POST":
        form_name = request.form.get("form_name")

        if form_name == "site_content":
            for section in SITE_CONTENT_SCHEMA:
                for field in section["fields"]:
                    key = field["key"]
                    if key in request.form:
                        SiteContent.query.filter_by(key=key).update(
                            {"value": request.form.get(key, "").strip()}
                        )
            db.session.commit()
            flash("サイト文章を更新しました。", "success")
            return redirect(url_for("admin_dashboard"))

        if form_name == "hero_image":
            file = request.files.get("hero_image")
            if not file or file.filename == "":
                flash("画像ファイルを選択してください。", "danger")
            else:
                saved_path = save_uploaded_file(file)
                if saved_path:
                    current = SiteContent.query.get(HERO_IMAGE_KEY)
                    old_path = current.value if current else HERO_IMAGE_DEFAULT
                    SiteContent.query.filter_by(key=HERO_IMAGE_KEY).update({"value": saved_path})
                    db.session.commit()
                    if old_path and old_path.startswith("images/uploads/"):
                        old_file = os.path.join(app.static_folder, old_path)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    flash("トップ画像を更新しました。", "success")
                else:
                    flash("アップロードできる画像形式は png / jpg / jpeg / gif / webp / svg です。", "danger")
            return redirect(url_for("admin_dashboard"))

        if form_name == "gallery_add":
            file = request.files.get("gallery_image")
            caption = request.form.get("gallery_caption", "").strip()
            if not file or file.filename == "":
                flash("画像ファイルを選択してください。", "danger")
            else:
                saved_path = save_uploaded_file(file)
                if saved_path and caption:
                    db.session.add(GalleryImage(filename=saved_path, caption=caption))
                    db.session.commit()
                    flash("ギャラリー画像を追加しました。", "success")
                else:
                    flash("画像とキャプションを入力してください。", "danger")
            return redirect(url_for("admin_dashboard"))

        if form_name == "gallery_delete":
            image_id = request.form.get("image_id")
            image = GalleryImage.query.get(image_id)
            if image:
                image_path = os.path.join(app.static_folder, image.filename)
                db.session.delete(image)
                db.session.commit()
                if image.filename.startswith("images/uploads/") and os.path.exists(image_path):
                    os.remove(image_path)
                flash("ギャラリー画像を削除しました。", "info")
            else:
                flash("画像が見つかりませんでした。", "warning")
            return redirect(url_for("admin_dashboard"))

        if form_name == "update_password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            user = AdminUser.query.get(session.get("admin_user_id"))
            if not user or not user.check_password(current_password):
                flash("現在のパスワードが正しくありません。", "danger")
            elif not new_password or len(new_password) < 8:
                flash("新しいパスワードは8文字以上にしてください。", "danger")
            elif new_password != confirm_password:
                flash("新しいパスワードが一致しません。", "danger")
            else:
                user.set_password(new_password)
                db.session.commit()
                flash("パスワードを更新しました。", "success")
            return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin/dashboard.html",
        content=content,
        schema=SITE_CONTENT_SCHEMA,
        hero_image=url_for("static", filename=content.get(HERO_IMAGE_KEY, HERO_IMAGE_DEFAULT)),
        gallery_images=gallery_images,
    )


with app.app_context():
    db.create_all()
    seed_defaults()


if __name__ == "__main__":
    app.run(debug=True)
