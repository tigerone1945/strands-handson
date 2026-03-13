# 必要なライブラリをインポート
import os
import feedparser
from strands import Agent, tool
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

# BedrockモデルIDは環境変数で上書き可能
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-lite-v1:0")

# ツールを定義
@tool
def get_aws_updates(service_name: str) -> list:
    # AWS What's NewのRSSフィードをパース
    feed = feedparser.parse("https://aws.amazon.com/about-aws/whats-new/recent/feed/")    
    result = []

    # フィードの各エントリをチェック
    for entry in feed.entries:
        # 件名にサービス名が含まれているかチェック
        if service_name.lower() in entry.title.lower():
            result.append({
                "published": entry.get("published", "N/A"),
                "summary": entry.get("summary", "")
            })
            
            # 最大3件のエントリを取得
            if len(result) >= 3:
                break

    return result

# エージェントを作成
agent = Agent(
    model=MODEL_ID,
    tools=[get_aws_updates]
)

# ユーザー入力を取得
service_name = input("アップデートを知りたいAWSサービス名を入力してください: ").strip()

# プロンプトを指定してエージェントを起動
prompt = f"AWSの{service_name}の最新アップデートを、日付つきで要約して。"
try:
    response = agent(prompt)
    print(response)
except Exception as e:
    error_text = str(e)
    if "Legacy" in error_text or "Access denied" in error_text:
        print("モデルにアクセスできません。`BEDROCK_MODEL_ID` を有効なモデルに変更してください。")
        print(f"現在のモデル: {MODEL_ID}")
    else:
        raise
