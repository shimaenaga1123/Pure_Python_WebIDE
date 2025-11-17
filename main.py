import platform

if platform.system() == "Emscripten":
    import asyncio
    import sys
    import time
    import traceback
    from io import StringIO

    import jedi
    from js import document, window
    from pyodide.ffi import create_proxy, to_js

    EditorView = window.EditorView
    basicSetup = window.basicSetup
    python_lang = window.python_lang
    autocompletion = window.autocompletion
    linter = window.linter
    vsCodeDark = window.vsCodeDark

    # UI 요소들
    editor_container = document.getElementById("editor")
    output_element = document.getElementById("output")
    status_element = document.getElementById("status")
    exec_time_element = document.getElementById("execTime")
    loading_element = document.getElementById("loading")

    # 입력 Promise resolver 저장용
    input_resolver = None
    current_input_element = None

    def get_line_col(text, offset):
        line = 1
        col = 0
        for i in range(min(offset, len(text))):
            if text[i] == "\n":
                line += 1
                col = 0
            else:
                col += 1
        return line, col

    def pos_to_offset(text, line, col):
        lines = text.split("\n")
        offset = 0
        for i in range(min(line, len(lines))):
            if i < line:
                offset += len(lines[i]) + 1
            else:
                offset += min(col, len(lines[i]))
        return offset

    def get_completions(code, pos):
        line, col = get_line_col(code, pos)
        script = jedi.Script(code)
        completions = script.complete(line, col)

        result = []
        for completion in completions[:20]:
            result.append(
                {
                    "label": completion.name,
                    "type": completion.type,
                    "info": completion.docstring(raw=True)[:200]
                    if completion.docstring(raw=True)
                    else "",
                }
            )
        return result

    def get_diagnostics(code):
        errors = []
        try:
            compile(code, "<string>", "exec")
        except SyntaxError as e:
            errors.append(
                {
                    "line": (e.lineno - 1) if e.lineno else 0,
                    "col": (e.offset - 1) if e.offset else 0,
                    "message": str(e.msg),
                    "severity": "error",
                }
            )
        except Exception as e:
            errors.append({"line": 0, "col": 0, "message": str(e), "severity": "error"})
        return errors

    def python_completions_handler(context):
        code = context.state.doc.toString()
        pos = context.pos

        word_start = pos
        while word_start > 0:
            char = code[word_start - 1]
            if not (char.isalnum() or char == "_"):
                break
            word_start -= 1

        completions = get_completions(code, pos)

        if not completions:
            return None

        options = []
        for c in completions:
            options.append(
                to_js({"label": c["label"], "type": c["type"], "info": c["info"]})
            )

        return to_js({"from": word_start, "to": pos, "options": to_js(options)})

    def python_linter_handler(view):
        code = view.state.doc.toString()
        diagnostics = get_diagnostics(code)

        result = []
        for d in diagnostics:
            offset_from = pos_to_offset(code, d["line"], d["col"])
            offset_to = pos_to_offset(code, d["line"], d["col"] + 1)

            result.append(
                to_js(
                    {
                        "from": offset_from,
                        "to": offset_to,
                        "severity": d["severity"],
                        "message": d["message"],
                    }
                )
            )

        return to_js(result)

    completions_proxy = create_proxy(python_completions_handler)
    linter_proxy = create_proxy(python_linter_handler)

    initial_code = r"""# 인터랙티브 입력 예제
name = input("이름을 입력하세요: ")
age = input("나이를 입력하세요: ")

print(f"\n안녕하세요, {name}님!")
print(f"당신은 {age}살이군요.")

# 간단한 계산기
import math
num = float(input("\n제곱근을 구할 숫자: "))
result = math.sqrt(num)
print(f"sqrt({num}) = {result}")"""

    extensions = to_js(
        [
            basicSetup,
            python_lang(),
            autocompletion(to_js({"override": to_js([completions_proxy])})),
            linter(linter_proxy, to_js({"delay": 500})),
            vsCodeDark,
        ]
    )

    view = EditorView.new(
        to_js(
            {"doc": initial_code, "parent": editor_container, "extensions": extensions}
        )
    )

    # 터미널 출력에 텍스트 추가하는 함수
    def append_to_terminal(text, scroll=True):
        # 텍스트 노드 생성
        text_node = document.createTextNode(text)
        output_element.appendChild(text_node)

        if scroll:
            output_element.scrollTop = output_element.scrollHeight

    async def custom_input(prompt=""):
        global input_resolver, current_input_element

        # 프롬프트를 터미널에 표시 (줄바꿈 없이)
        if prompt:
            prompt_node = document.createTextNode(prompt)
            output_element.appendChild(prompt_node)

        # 인라인 input 요소 생성
        input_elem = document.createElement("input")
        input_elem.type = "text"
        input_elem.className = "inline-input"
        input_elem.autocomplete = "off"
        input_elem.spellcheck = False

        # Enter 키 이벤트 리스너
        def handle_keypress(event):
            if event.key == "Enter":
                global input_resolver
                if input_resolver:
                    value = input_elem.value
                    input_resolver(value)
                    input_resolver = None

        input_elem.addEventListener("keypress", create_proxy(handle_keypress))

        # input 요소를 출력 영역에 추가
        output_element.appendChild(input_elem)
        current_input_element = input_elem

        # 포커스 설정
        input_elem.focus()

        # Promise를 사용하여 입력 대기
        from js import Promise

        def executor(resolve, reject):
            global input_resolver
            input_resolver = resolve

        promise = Promise.new(executor)
        result = await promise

        # input 요소를 텍스트로 교체
        input_value = input_elem.value
        output_element.removeChild(input_elem)

        # 입력값을 텍스트로 표시하고 줄바꿈
        value_node = document.createTextNode(input_value + "\n")
        output_element.appendChild(value_node)

        current_input_element = None

        # 스크롤
        output_element.scrollTop = output_element.scrollHeight

        return result

    # 실시간 터미널 출력을 위한 커스텀 stdout/stderr 클래스
    class TerminalOutputStream:
        def __init__(self, is_error=False):
            self.is_error = is_error
            self.buffer = []

        def write(self, text):
            if text:
                # 실시간으로 터미널에 출력
                append_to_terminal(text, scroll=True)
                # 나중에 참조하기 위해 버퍼에도 저장
                self.buffer.append(text)

        def flush(self):
            pass

        def getvalue(self):
            return "".join(self.buffer)

    # Python 코드 실행 함수
    async def run_code(event):
        code = view.state.doc.toString()

        # 실시간 출력을 위한 커스텀 stdout/stderr 설정
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = TerminalOutputStream()
        redirected_error = TerminalOutputStream(is_error=True)

        sys.stdout = redirected_output
        sys.stderr = redirected_error

        status_element.textContent = "실행 중..."
        status_element.style.color = "#ff9800"

        # 터미널 초기화
        output_element.innerHTML = ""

        start_time = time.time()

        try:
            # 코드 실행 환경에 커스텀 input 함수 추가
            import builtins
            import re

            old_input = builtins.input
            builtins.input = custom_input

            # 사용자 코드에서 input() 호출을 (await input())으로 변환
            # input(...)을 찾아서 (await input(...))으로 변경
            def transform_input_calls(code):
                result = []
                i = 0
                while i < len(code):
                    # input( 패턴 찾기
                    match = re.search(r"\binput\s*\(", code[i:])
                    if not match:
                        result.append(code[i:])
                        break

                    # 매치 이전 부분 추가
                    result.append(code[i : i + match.start()])

                    # (await input( 추가
                    result.append("(await input(")

                    # 여는 괄호 위치
                    paren_start = i + match.end()

                    # 매칭되는 닫는 괄호 찾기
                    paren_count = 1
                    j = paren_start
                    in_string = False
                    string_char = None

                    while j < len(code) and paren_count > 0:
                        char = code[j]

                        # 문자열 처리
                        if char in ['"', "'"]:
                            if not in_string:
                                in_string = True
                                string_char = char
                            elif char == string_char and (
                                j == 0 or code[j - 1] != "\\"
                            ):
                                in_string = False
                                string_char = None

                        # 괄호 카운트 (문자열 밖에서만)
                        elif not in_string:
                            if char == "(":
                                paren_count += 1
                            elif char == ")":
                                paren_count -= 1

                        j += 1

                    # input의 인자 부분 추가
                    result.append(code[paren_start : j - 1])

                    # 닫는 괄호 두 개 추가 (input의 괄호 + await의 괄호)
                    result.append("))")

                    i = j

                return "".join(result)

            transformed_code = transform_input_calls(code)

            if transformed_code.strip() == "":
                transformed_code = "pass"

            # 사용자 코드를 async 함수로 래핑
            # 각 라인에 들여쓰기 추가
            indented_code = "\n".join(
                "    " + line for line in transformed_code.split("\n")
            )
            wrapped_code = f"""async def __user_main__():
{indented_code}
"""

            # 실행 환경 설정
            exec_globals = {
                "__name__": "__main__",
                "__builtins__": builtins,
                "__import__": lambda name: __import__(name) if name != "js" else None,
            }

            # 래핑된 코드 실행
            exec(wrapped_code, exec_globals)

            # __user_main__ 함수 실행
            await exec_globals["__user_main__"]()

            # 출력 확인 (이미 실시간으로 표시됨)
            stdout_value = redirected_output.getvalue()
            stderr_value = redirected_error.getvalue()

            # 출력이 전혀 없었을 경우에만 메시지 표시
            if not stdout_value and not stderr_value:
                append_to_terminal("(출력 없음)\n", scroll=True)

            elapsed = time.time() - start_time
            status_element.textContent = "실행 완료"
            status_element.style.color = "#4CAF50"
            exec_time_element.textContent = f"{elapsed:.3f}초"

            # input 함수 복원
            builtins.input = old_input

        except Exception as e:
            # 에러 출력 (이미 실시간으로 표시된 stderr 위에 추가)
            error_output = redirected_error.getvalue()

            # traceback만 추가로 출력
            append_to_terminal("\n=== 에러 발생 ===\n", scroll=True)
            append_to_terminal(traceback.format_exc() + "\n", scroll=True)

            status_element.textContent = "에러 발생"
            status_element.style.color = "#f44336"
            exec_time_element.textContent = ""

            # 현재 입력 요소 제거 (에러 시)
            global current_input_element
            if current_input_element:
                try:
                    output_element.removeChild(current_input_element)
                    current_input_element = None
                except:
                    pass

            # input 함수 복원 (에러 시에도)
            import builtins

            try:
                builtins.input = old_input
            except:
                pass

        finally:
            # stdout, stderr 복원
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    # 에디터 지우기 함수
    def clear_editor(event):
        view.dispatch(
            to_js(
                {
                    "changes": to_js(
                        {"from": 0, "to": view.state.doc.length, "insert": ""}
                    )
                }
            )
        )
        status_element.textContent = "에디터 초기화됨"
        status_element.style.color = "#5f6368"

    # 출력 지우기 함수
    def clear_output(event):
        global current_input_element
        output_element.innerHTML = ""
        status_element.textContent = "준비"
        status_element.style.color = "#5f6368"
        exec_time_element.textContent = ""
        current_input_element = None

    # 버튼 이벤트 리스너 등록
    run_btn = document.getElementById("runBtn")
    clear_btn = document.getElementById("clearBtn")
    clear_output_btn = document.getElementById("clearOutputBtn")

    run_btn.addEventListener("click", create_proxy(run_code))
    clear_btn.addEventListener("click", create_proxy(clear_editor))
    clear_output_btn.addEventListener("click", create_proxy(clear_output))

    # 로딩 화면 숨기기
    loading_element.classList.add("hidden")

    # 초기화 완료 상태 표시
    status_element.textContent = "준비 완료"
    status_element.style.color = "#4CAF50"

    async def show_ready():
        await asyncio.sleep(1)
        status_element.textContent = "준비"
        status_element.style.color = "#5f6368"

    asyncio.create_task(show_ready())
else:
    import os

    try:
        from bottle import route, run, static_file, template
    except ImportError:
        import pip

        pip.main(["install", "bottle"])
        from bottle import route, run, static_file, template

    @route("/")
    def main():
        return template("index.html", filename=os.path.basename(__file__))

    @route("/<path:path>")
    def get_static(path):
        return static_file(path, root="")

    if __name__ == "__main__":
        run(host="localhost", port=3000, debug=True, reloader=True)
