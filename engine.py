# engine.py — CLIブリッジ版
# 既存の print/input ベースのゲームをWebで一歩ずつ進めるためのアダプタ。
# 使い方：
#   1) 自分のエントリポイントに合わせて ENTRYPOINT を1行だけ書き換える
#   2) 他は触らなくてOK。既存の *.py はそのままリポジトリに入れる

import builtins
import threading
import queue
import time
import sys
from types import SimpleNamespace

# ==== ここをあなたのエントリポイントに合わせて変更 ====
# 例1: あなたの main.py に def main(): がある場合
from main import main as ENTRYPOINT
# 例2: あるモードだけを走らせたいなら:
# from mtdlp_mode import start_mtdlp_mode as ENTRYPOINT
# =======================================================

# スレッド間共有（セッションごとに持つ前提：Flask側はセッションでstateを分離）
class _CliBridge:
    def __init__(self):
        self.input_q = queue.Queue()     # ブラウザ→CLI（ユーザー入力）
        self.output_q = queue.Queue()    # CLI→ブラウザ（print出力）
        self.thread = None
        self.started = False
        self.finished = False
        self.lock = threading.Lock()
        self._orig_input = builtins.input
        self._orig_print = builtins.print

    def _patched_input(self, prompt=""):
        # promptも出力として拾う
        if prompt:
            self.output_q.put(prompt)
        # 次のユーザー入力が来るまでブロック
        val = self.input_q.get()  # step() が put するまで待つ
        return val

    def _patched_print(self, *args, **kwargs):
        # print内容を文字列にしてキューに入れる
        end = kwargs.get("end", "\n")
        sep = kwargs.get("sep", " ")
        text = sep.join(str(a) for a in args) + end
        self.output_q.put(text)

    def _worker(self):
        try:
            builtins.input = self._patched_input
            builtins.print = self._patched_print
            # エントリポイント実行（既存のCLIがここで動く）
            ENTRYPOINT()
        except SystemExit:
            pass
        except Exception as e:
            self.output_q.put(f"[エラー] {e}\n")
        finally:
            # 復元
            builtins.input = self._orig_input
            builtins.print = self._orig_print
            with self.lock:
                self.finished = True

    def start_if_needed(self):
        with self.lock:
            if not self.started:
                self.thread = threading.Thread(target=self._worker, daemon=True)
                self.thread.start()
                self.started = True

    def push_user_input(self, s: str):
        # ブラウザからの入力を投入
        self.input_q.put(s)

    def drain_output(self, timeout=0.2):
        """一定時間待ちながら、CLI側で溜まった出力をまとめて取り出す"""
        buf = []
        # 少し待ってから連続で吸い出す
        end_time = time.time() + timeout
        while True:
            remaining = end_time - time.time()
            try:
                line = self.output_q.get(timeout=max(0.01, remaining))
                buf.append(line)
            except queue.Empty:
                break
        return "".join(buf)

# Flaskセッションごとに1つ持てるよう、状態はシリアライズ可能な最低限だけにする
def initial_state():
    return {"started": False, "finished": False}

# グローバルにブリッジ実体を置く（プロセス内で共有）。
# Flaskのsessionでユーザごとに分離されるので、ブラウザのセッション単位で使えばOK。
_BRIDGE = _CliBridge()

def step(state, user_input: str):
    # 1) 初回はスレッド起動して、CLIの最初の出力（最初のinput前まで）を回収
    if not state.get("started"):
        _BRIDGE.start_if_needed()
        state["started"] = True
        # 少し待って最初の出力をまとめて取る
        time.sleep(0.15)
        out = _BRIDGE.drain_output(timeout=0.3)
        state["finished"] = _BRIDGE.finished
        return (out, state)

    # 2) 2回目以降：ユーザー入力を渡して、次のプロンプト/出力が溜まるのを少し待つ
    if user_input is not None:
        _BRIDGE.push_user_input(user_input)

    # CLIが次の input() に到達する or 終了するまでの出力を回収
    time.sleep(0.1)
    out = _BRIDGE.drain_output(timeout=0.4)
    state["finished"] = _BRIDGE.finished

    # 終了していて出力が空なら、お別れメッセージ（任意）
    if state["finished"] and not out.strip():
        out = "＜シナリオ終了＞\nページ上部のリセットで最初から再開できます。"

    return (out, state)
