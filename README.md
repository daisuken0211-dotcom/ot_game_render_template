# 作業療法ゲーム（Render公開用テンプレート）

このテンプレートは、既存の **CLI（print/input）ベースのPythonゲーム** を
**Flask Webアプリ** として簡単に公開するための最小構成です。

## 使い方（ローカル）

```bash
pip install -r requirements.txt
python app.py
# ブラウザで http://localhost:8000 を開く
```

## Render での公開手順

1. このフォルダ一式を GitHub リポジトリに push（例：`ot-game-onrender`）
2. Render にログイン → New → **Web Service**
3. 対象リポジトリを選択し、以下を設定
   - Env: **Python**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: **Free**
4. Deploy を実行 → 数分後に URL が発行されます。

> `render.yaml` がある場合、自動で設定が読み込まれます。

## 既存ゲームの統合方法

- `engine.py` の `initial_state` と `step` を、あなたのロジックに合わせて置き換えてください。
- もし既存コードが `input()` や `print()` を多用している場合は、
  1) それらの箇所を関数化（1ステップの入出力に分解）して `step()` から呼ぶ、
  2) あるいは内部で「状態マシン」を用意し、`user_input` を受けて次の出力テキストを返す形に作り替える、
  のどちらかが簡単です。

## 補足
- 無料プランでは15分アクセスが無いとスリープします。次のアクセスで自動復帰します。
- 常時稼働したい場合のみ、有料プランへ（最小 \$7/月 目安）。
