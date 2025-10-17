# engine.py
# Replace this simple demo engine with hooks into your actual CLI game.
# Minimal contract:
#   - initial_state() -> dict  # any JSON-serializable state
#   - step(state, user_input) -> (output_text:str, new_state:dict)

def initial_state():
    return {
        "scene": "menu",
        "step": 0,
    }


def step(state, user_input):
    scene = state.get("scene", "menu")
    step_num = state.get("step", 0)

    if scene == "menu":
        if step_num == 0:
            state["step"] = 1
            return (
                "ようこそ！作業療法ゲーム（Web版デモ）へ。\n"
                "次のモードから選んで番号を入力してください：\n"
                "1) MTDLPモード\n"
                "2) 目標合意モード\n"
                "3) 介入設計モード\n"
                "（数字を入力して送信）",
                state
            )
        else:
            choice = (user_input or "").strip()
            if choice == "1":
                state["scene"] = "mtdlp"
                state["step"] = 0
                return ("MTDLPモードを開始します。氏名（例：山口さん）を入力してください。", state)
            elif choice == "2":
                state["scene"] = "goal"
                state["step"] = 0
                return ("目標合意モードを開始します。生活目標を1つ入力してください。", state)
            elif choice == "3":
                state["scene"] = "intervention"
                state["step"] = 0
                return ("介入設計モードを開始します。対象の課題を1つ入力してください。", state)
            else:
                return ("1〜3の数字を入力してください。", state)

    if scene == "mtdlp":
        if step_num == 0:
            state["name"] = user_input or "山口さん"
            state["step"] = 1
            return (f"{state['name']}ですね。最近の生活の困りごとを1つ入力してください。", state)
        elif step_num == 1:
            state["problem"] = user_input or "通勤時の不安"
            state["step"] = 2
            return ("その困りごとに対して、あなたが大切にしたい価値観（例：自立・安心・役割継続）を1つ入力してください。", state)
        else:
            value = user_input or "安心"
            state["step"] = 0
            state["scene"] = "menu"
            summary = (
                f"MTDLP要約：\n"
                f"- 対象者：{state.get('name')}\n"
                f"- 生活上の困りごと：{state.get('problem')}\n"
                f"- 重視する価値：{value}\n"
                "→ この要約はあくまでデモです。実アプリでは既存ロジックに差し替えてください。\n\n"
                "メニューに戻りました。1〜3を入力してください。"
            )
            return (summary, state)

    if scene == "goal":
        if step_num == 0:
            state["goal"] = user_input or "週5日バス通勤"
            state["step"] = 1
            return ("その目標をいつまでに達成したいですか？（例：2025-12-31）", state)
        else:
            state["deadline"] = user_input or "2025-12-31"
            state["scene"] = "menu"
            state["step"] = 0
            return (
                f"目標合意メモ：{state['goal']}（目標期限：{state['deadline']}）\n"
                "メニューに戻りました。1〜3を入力してください。",
                state
            )

    if scene == "intervention":
        if step_num == 0:
            state["issue"] = user_input or "移動時のふらつき"
            state["step"] = 1
            return ("この課題に対して、環境・人・作業のどれを優先して整えますか？（例：環境）", state)
        else:
            choice = (user_input or "環境").strip()
            state["scene"] = "menu"
            state["step"] = 0
            return (
                f"介入設計メモ：課題={state['issue']} / 優先整備={choice}\n"
                "メニューに戻りました。1〜3を入力してください。",
                state
            )

    # fallback
    state["scene"] = "menu"
    state["step"] = 1
    return ("メニューに戻りました。1〜3の数字を入力してください。", state)
