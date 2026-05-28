import streamlit as st
import requests
import textwrap
import os
# from dotenv import load_dotenv

# load_dotenv()

def get_gemini_models(api_key):
    try:
        # モデル一覧を取得するエンドポイント
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(list_url)
        if res.status_code == 200:
            data = res.json()
            # generateContent（テキスト生成）に対応しているモデルのみを抽出
            models = [
                m["name"] for m in data.get("models", []) 
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            return models
        else:
            return []
    except Exception:
        return []

# 1. ページの基本設定（ブラウザのタブに表示される名前やアイコン）
st.set_page_config(page_title="日⇒英　英訳ツール", layout="centered")

# 2. 画面のタイトルと説明文
st.title("日⇒英　英訳ツール")
st.write("簡単な日本語を入力するだけで、国際会議で利用可能なレベルでの英訳を生成します")

# 3. APIキーの読み込み（ローカル用の.env、またはStreamlit CloudのSecrets機能から自動取得）
# os.environ.getは、システムに保存された環境変数の値を取り出す関数です
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
# api_key=os.getenv("GEMINI_API_KEY") #.envファイルからAPIキーを取得

selected_model = None
if api_key:
    with st.spinner("利用可能なGeminiモデルを確認中..."):
        available_models = get_gemini_models(api_key)
    
    if available_models:
        # デフォルトで「gemini-3.1-flash-lite」や「gemini-2.5-flash」などがあればそれを初期値にするロジック
        default_index = 0
        for i, m in enumerate(available_models):
            if "gemini-3.1-flash-lite" in m:
                default_index = i
                break
        
        selected_model = st.selectbox(
            "使用するAIモデルを選択してください（APIから自動取得）",
            options=available_models,
            index=default_index
        )
    else:
        st.warning("モデル一覧の取得に失敗しました。デフォルトのモデルを使用します。")
        selected_model = "models/gemini-3.1-flash-lite"
else:
    st.error("APIキーが設定されていないため、モデル一覧を取得できません。")

# 4. ユーザーからの入力を受け付けるテキストエリア
user_input = st.text_area("英訳したい日本語を入力してください", placeholder="例：今日はいい天気ですね", height=100)

level_instruction = None
transration_level = st.selectbox(
    "翻訳レベルを選択してください",
    ("中学生レベル", "高校生レベル", "ネイティブ・論文レベル")
)

if transration_level == "中学生レベル":
    level_instruction = """
    - 複雑な内容を中学生レベルの英語（簡潔な語彙と短い文章構成）で書き換え、国際会議の聴衆が直感的に理解できるようにする必要があります。
    - 語彙は英検3級〜準2級程度の範囲に抑え、一文を短く（15語以内を目安に）構成する。
    - 難しい仮定法や複雑な関係代名詞の多用を避け、S+V+O（主語・動詞・目的語）の基本構造を重視すること。
    - 専門用語を使用する場合は、その直後に平易な言葉での短い説明を加えること（例: "Hyper-parameter, which is a setting for the AI, ..."）。
    """
elif transration_level == "高校生レベル":
    level_instruction = """
    - 高等学校卒業〜大学基礎レベルの英語（英検2級〜準1級程度）で書き換え、論理的かつスムーズに伝わる文章にしてください。
    - 一文は長すぎず（20語前後を目安に）、適切な接続詞（However, Therefore, In addition など）を用いて論理の展開を明確にする。
    - 学術的な文脈で一般的に使われる標準的な語彙や構文（関係代名詞や分詞構文など）は適切に使用して構いません。
    """
else:
    level_instruction = """
    - 国際的なトップジャーナルや主要な学会でそのまま通用する、格調高く自然なアカデミック英語（英検1級・ネイティブレベル）に変換してください。
    - 単なる直訳ではなく、分野特有のコロケーション（語の組み合わせ）や、洗練された学術的語彙（例: analyze, facilitate, implementation など）を駆使する。
    - 冗長な表現を避け、簡潔でありながら受動態や名詞化表現を巧みに用いた、フォーマルで知的な文章構成にしてください。
    """

# 5. 生成ボタンが押されたときの処理
if st.button("英訳を開始する", type="primary"):
    if not api_key:
        st.error("APIキーが設定されていません。環境変数またはStreamlit Secretsを設定してください。")
    elif not user_input.strip():
        st.warning("指示を入力してください。")
    else:
        # st.spinnerを使うと、処理中にぐるぐる回るローディングアニメーションが出ます
        with st.spinner("AIがプロンプトを構造化しています..."):
            try:
                # Geminiのモデル選択はここ！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！
                # Gemini APIのエンドポイントURL（モデルは最新のgemini-3.1-flash-lite）
                url = f"https://generativelanguage.googleapis.com/v1beta/{selected_model}:generateContent?key={api_key}"
                
                # AIへ渡すメタプロンプトの組み立て
                meta_prompt = textwrap.dedent(f"""
                                                # Role
                                                あなたは国際的な学術会議のプレゼンテーションおよび論文投稿を専門とする「アカデミック・コミュニケーション・アドバイザー」です。
                                                専門的な内容を、聴衆や読者に最も効果的に伝えるための表現に変換するエキスパートです。

                                                # Context
                                                学術的なトピックを英語で発表・執筆する際、ターゲット層や媒体に合わせた適切な言語レベルの選択が極めて重要です。
                                                今回は、指定されたレベルに合わせて文章を最適化する必要があります。

                                                # Task
                                                [ ] で囲まれた日本語の文章を読み取り、以下の手順で英訳・調整してください。

                                                1. **直訳的思考の排除:** 日本語特有の曖昧さや過度な謙遜表現を排除し、論理的な骨子を抽出する。
                                                2. **言語レベルの調整:** 以下の【言語レベルの指定】に厳格に従って英語を構成する。
                                                3. **推敲:** 指定されたレベルにおいて、表現が正確かつ自然に伝わっているか確認し、修正する。

                                                # 【言語レベルの指定】
                                                {level_instruction}

                                                # Constraints
                                                - 文法的に正確であること。
                                                - 日本語の元のニュアンスを壊さないこと。

                                                # Output Style & Format (重要)
                                                - 出力は必ず以下の構成にし、英語訳と解説の間には「---SPLIT---」という区切り文字列だけを入れた行を挟んでください。
                                                - AIとしての挨拶、前置き、結びの言葉（「承知しました」「いかがでしょうか」など）は一切出力しないでください。

                                                [生成した英語訳（ここには解説などを一切含めない）]
                                                ---SPLIT---
                                                💡 この英語訳のポイント
                                                [なぜそのような構成（語彙・構文の選択）にしたかの解説テキスト]

                                                英語訳を行う日本語: [{user_input}]""")

                # APIへ送信するデータの形を定義
                payload = {
                    "contents": [{
                        "parts": [{"text": meta_prompt}]
                    }]
                }
                
                # requestsライブラリを使ってAPIにデータを送信（POSTリクエスト）
                response = requests.post(url, json=payload)
                response_data = response.json()
                
                if response.status_code == 200:
                    # 成功したらテキストを抽出
                    generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]

                    # 区切り文字で「プロンプト本体」と「解説」に分割する
                    if "---SPLIT---" in generated_text:
                        prompt_body, prompt_points = generated_text.split("---SPLIT---", 1)
                    else:
                        prompt_body = generated_text
                        prompt_points = ""

                    st.success("生成が完了しました！")
                    
                    # 生成されたプロンプトをテキストエリアに表示
                    st.text_area("テキストとして選択・確認用", value=generated_text, height=250)
                    
                    # 【重要】st.codeを使うと、標準で画面右上に一発コピーボタンが自動配置されます
                    st.write("👇 下の枠の右上にあるボタンからワンクリックでコピーできます")
                    st.code(prompt_body.strip(), language="markdown")
                    
                else:
                    error_msg = response_data.get("error", {}).get("message", "不明なエラー")
                    st.error(f"Gemini APIエラー: {error_msg}")
            except Exception as e:
                st.error(f"通信中にエラーが発生しました: {str(e)}")