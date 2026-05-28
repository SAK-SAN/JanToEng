import streamlit as st
import requests
import textwrap
import os
# from dotenv import load_dotenv

# load_dotenv()

# 1. ページの基本設定（ブラウザのタブに表示される名前やアイコン）
st.set_page_config(page_title="日⇒英　英訳ツール", layout="centered")

# 2. 画面のタイトルと説明文
st.title("日⇒英　英訳ツール")
st.write("簡単な日本語を入力するだけで、国際会議で利用可能なレベルでの英訳を生成します")

# 3. APIキーの読み込み（ローカル用の.env、またはStreamlit CloudのSecrets機能から自動取得）
# os.environ.getは、システムに保存された環境変数の値を取り出す関数です
api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
# api_key=os.getenv("GEMINI_API_KEY") #.envファイルからAPIキーを取得

# 4. ユーザーからの入力を受け付けるテキストエリア
user_input = st.text_area("英訳したい日本語を入力してください", placeholder="例：今日はいい天気ですね", height=100)

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
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
                
                # AIへ渡すメタプロンプトの組み立て
                meta_prompt = textwrap.dedent(f"""
                                                # Role
                                                あなたは国際的な学術会議のプレゼンテーションおよび論文投稿を専門とする「アカデミック・コミュニケーション・アドバイザー」です。
                                                専門的な内容を、英語を母国語としない聴衆にも明快に伝えるための平易かつ正確な表現に変換するエキスパートです。

                                                # Context
                                                学術的なトピックを英語で発表・執筆する際、高度な専門用語や複雑な構文は、しばしば意図を誤解させる原因となります。
                                                今回は、複雑な内容を中学生レベルの英語（簡潔な語彙と短い文章構成）で書き換え、国際会議の聴衆が直感的に理解できるようにする必要があります。

                                                # Task
                                                [ ] で囲まれた日本語の文章を読み取り、以下の手順で英訳・調整してください。

                                                1. **直訳的思考の排除:** 日本語特有の曖昧さや過度な謙遜表現を排除し、論理的な骨子を抽出する。
                                                2. **言語レベルの調整:** 語彙は英検3級〜準2級程度の範囲に抑え、一文を短く（15語以内を目安に）構成する。
                                                3. **推敲:** 専門的な内容が平易な言葉で正確に伝わっているか確認し、自然な英語表現に修正する。

                                                # Constraints
                                                - 文法的に正確であること。
                                                - 専門用語を使用する場合は、その直後に平易な言葉での短い説明を加えること（例: "Hyper-parameter, which is a setting for the AI, ..."）。
                                                - 難しい仮定法や複雑な関係代名詞の多用を避け、S+V+O（主語・動詞・目的語）の基本構造を重視すること。
                                                - 日本語の元のニュアンスを壊さないこと。

                                                # Output Style & Format (重要)
                                                - 出力は必ず以下の構成にし、英語訳と解説の間には「---SPLIT---」という区切り文字列だけを入れた行を挟んでください。
                                                - AIとしての挨拶、前置き、結びの言葉（「承知しました」「いかがでしょうか」など）は一切出力しないでください。

                                                [生成した英語訳（ここには解説などを一切含めない）]
                                                ---SPLIT---
                                                💡 この英語訳のポイント
                                                [なぜそのような構成にしたかの解説テキスト]
                                                                                                                    
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