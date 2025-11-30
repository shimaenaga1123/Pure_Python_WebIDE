import platform  # 플랫폼 감지를 위한 내장 라이브러리

if platform.system() != "Emscripten":  # 백엔드 코드 시작
    import asyncio  # 비동기 처리를 위한 내장 라이브러리
    import webbrowser  # 자동 브라우저 실행을 위한 내장 라이브러리

    try:
        from bottle import route, run, template  # 백엔드 프레임워크(Flask와 유사)
    except ImportError:  # 자동 설치 코드
        import pip

        pip.main(["install", "bottle"])
        from bottle import route, run, template

    @route("/")  # / 요청시 HTML 페이지 반환
    def index():
        return template(
            """
<!doctype html>
<html lang="ko">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Python IDE</title>
        <script src="https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.js"></script>
        <script type="module">
            import { EditorView, basicSetup } from "https://esm.sh/codemirror";
            import { python } from "https://esm.sh/@codemirror/lang-python";
            import { autocompletion } from "https://esm.sh/@codemirror/autocomplete";
            import { linter } from "https://esm.sh/@codemirror/lint";
            import { vsCodeDark } from "https://esm.sh/@fsegurai/codemirror-theme-vscode-dark";

            const pyodide = await loadPyodide();

            window.EditorView = EditorView;
            window.basicSetup = basicSetup;
            window.python_lang = python;
            window.autocompletion = autocompletion;
            window.linter = linter;
            window.pyodide = pyodide;
            window.vsCodeDark = vsCodeDark;

            await pyodide.loadPackage("micropip");
            await pyodide.loadPackage("jedi");

            await pyodide.runPythonAsync(
                await (await fetch("/main")).text(),
            );
        </script>

        <link href="https://shimaenaga1123.github.io/Pure_Python_WebIDE/style.css" rel="stylesheet" />
    </head>
    <body data-sveltekit-preload-data="hover">
        <div style="display: contents">
            <div class="loading svelte-1uha8ag" id="loading">
                <div class="loading-content svelte-1uha8ag">
                    <img
                        src="https://shimaenaga1123.github.io/Pure_Python_WebIDE/loading.svg"
                        alt="Loading..."
                        class="svelte-ruye1y center"
                    />
                    <div class="m3-font-body-large svelte-1uha8ag">
                        Python 환경 로딩 중...
                    </div>
                </div>
            </div>
            <div class="container svelte-1uha8ag">
                <header class="header svelte-1uha8ag">
                    <h1 class="m3-font-display-large svelte-1uha8ag">
                        Python IDE
                    </h1>
                    <p class="m3-font-body-medium svelte-1uha8ag">
                        인터랙티브 Python 실행 환경
                    </p>
                </header>
                <main class="main-content svelte-1uha8ag">
                    <div class="ide-layout svelte-1uha8ag">
                        <div
                            class="m3-container filled svelte-mxwuxu"
                            id="editor-section"
                        >
                            <div class="section-header svelte-1uha8ag">
                                <h2 class="m3-font-title-medium svelte-1uha8ag">
                                    코드 에디터
                                </h2>
                            </div>
                            <div
                                class="editor-wrapper svelte-1uha8ag"
                                id="editor"
                            ></div>
                            <div class="controls svelte-1uha8ag">
                                <button
                                    type="submit"
                                    class="m3-container filled s icon-none svelte-eefjof"
                                    id="runBtn"
                                >
                                    <div class="hitbox svelte-1q4u1kv"></div>
                                    <div
                                        class="ripple-container broken svelte-1q4u1kv"
                                    ></div>
                                    <div class="tint svelte-1q4u1kv"></div>
                                    실행
                                </button>
                                <button
                                    type="submit"
                                    class="m3-container tonal s icon-none svelte-eefjof"
                                    id="clearBtn"
                                >
                                    <div class="hitbox svelte-1q4u1kv"></div>
                                    <div
                                        class="ripple-container broken svelte-1q4u1kv"
                                    ></div>
                                    <div class="tint svelte-1q4u1kv"></div>
                                    초기화
                                </button>
                                <button
                                    type="submit"
                                    class="m3-container outlined s icon-none svelte-eefjof"
                                    id="clearOutputBtn"
                                >
                                    <div class="hitbox svelte-1q4u1kv"></div>
                                    <div
                                        class="ripple-container broken svelte-1q4u1kv"
                                    ></div>
                                    <div class="tint svelte-1q4u1kv"></div>
                                    출력 지우기
                                </button>
                            </div>
                            <div class="controls svelte-1uha8ag">
                                <div class="m3-container svelte-6b5eoq">
                                    <input
                                        class="focus-none m3-font-body-large svelte-6b5eoq"
                                        placeholder="패키지 이름"
                                        id="packageInput"
                                    />
                                </div>
                                <button
                                    type="submit"
                                    class="m3-container filled s icon-none svelte-eefjof"
                                    id="installBtn"
                                >
                                    <div class="hitbox svelte-1q4u1kv"></div>
                                    <div
                                        class="ripple-container broken svelte-1q4u1kv"
                                    ></div>
                                    <div class="tint svelte-1q4u1kv"></div>
                                    패키지 설치
                                </button>
                            </div>
                        </div>
                        <div
                            class="m3-container filled svelte-mxwuxu"
                            id="output-section"
                        >
                            <div class="section-header svelte-1uha8ag">
                                <h2 class="m3-font-title-medium svelte-1uha8ag">
                                    터미널
                                </h2>
                            </div>
                            <div class="terminal-wrapper svelte-1uha8ag">
                                <div
                                    class="output-content svelte-1uha8ag"
                                    id="output"
                                ></div>
                            </div>
                            <div class="status-bar svelte-1uha8ag">
                                <span
                                    class="m3-font-label-medium svelte-1uha8ag"
                                    id="status"
                                    >준비</span
                                >
                                <span
                                    class="m3-font-label-small svelte-1uha8ag"
                                    id="execTime"
                                ></span>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    </body>
</html>
            """,
        )

    @route("/main")  # /main 요청시 이 파일 자체를 반환
    def get_static():
        return open(__file__).read()

    async def main():  # 브라우저 자동 실행을 위한 함수
        await asyncio.sleep(1)
        webbrowser.open_new_tab("http://localhost:3000")

    if __name__ == "__main__":
        asyncio.run(main())
        run(host="localhost", port=3000)

else:  # 프론트엔드 코드 시작
    import asyncio  # 비동기 처리를 위한 내장 라이브러리
    import sys  # 시스템 빌트인 함수 관련 동작을 위한 내장 라이브러리
    import time  # 시간 관련 내장 라이브러리
    import traceback  # 에디터 내 오류 출력을 위한 내장 라이브러리

    import jedi  # 코드 자동완성을 위한 라이브러리(브라우저 내에서 설치됨)
    from js import (  # 브라우저를 제어하기 위한 내장 라이브러리(로컬에서 실행 불가하고 브라우저에서만 실행 가능)
        Promise,
        document,
        window,
    )
    from pyodide.ffi import (  # 브라우저와 데이터를 주고 받기 위한 내장 라이브러리(로컬에서 실행 불가하고 브라우저에서만 실행 가능)
        create_proxy,
        to_js,
    )

    # 자바스크립트 라이브러리 불러오기
    EditorView = window.EditorView
    basicSetup = window.basicSetup
    python_lang = window.python_lang
    autocompletion = window.autocompletion
    linter = window.linter
    vsCodeDark = window.vsCodeDark

    # HTML의 요소 가져오기
    editor_container = document.getElementById("editor")
    output_element = document.getElementById("output")
    status_element = document.getElementById("status")
    exec_time_element = document.getElementById("execTime")
    loading_element = document.getElementById("loading")

    input_resolver = None
    current_input_element = None

    # 자동완성과 오류 표시할 때 오프셋을 좌표로 변환하기 위한 함수
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

    # 자동완성과 오류 표시할 때 좌표를 오프셋으로 변환하기 위한 함수
    def pos_to_offset(text, line, col):
        lines = text.split("\n")
        offset = 0
        for i in range(min(line, len(lines))):
            if i < line:
                offset += len(lines[i]) + 1
            else:
                offset += min(col, len(lines[i]))
        return offset

    # 자동 완성을 가져오기 위한 함수
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

    # 오류를 가져오기 위한 함수
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

    # 자동 완성을 자바스크립트로 보내기 위한 함수
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

    # 오류를 자바스크립트로 보내기 위한 함수
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

    # 터미널에 글자를 쓰는 함수
    def append_to_terminal(text, scroll=True):
        text_node = document.createTextNode(text)
        output_element.appendChild(text_node)

        if scroll:
            output_element.scrollTop = output_element.scrollHeight

    # 터미널에서 입력을 받는 함수
    async def custom_input(prompt=""):
        global input_resolver, current_input_element

        if prompt:
            prompt_node = document.createTextNode(prompt)
            output_element.appendChild(prompt_node)

        input_elem = document.createElement("input")
        input_elem.type = "text"
        input_elem.className = "inline-input"
        input_elem.autocomplete = "off"
        input_elem.spellcheck = False

        def handle_keypress(event):
            if event.key == "Enter":
                global input_resolver
                if input_resolver:
                    value = input_elem.value
                    input_resolver(value)
                    input_resolver = None

        input_elem.addEventListener("keypress", create_proxy(handle_keypress))

        output_element.appendChild(input_elem)
        current_input_element = input_elem

        input_elem.focus()

        def executor(resolve, reject):
            global input_resolver
            input_resolver = resolve

        promise = Promise.new(executor)
        result = await promise

        input_value = input_elem.value
        output_element.removeChild(input_elem)

        value_node = document.createTextNode(input_value + "\n")
        output_element.appendChild(value_node)

        current_input_element = None

        output_element.scrollTop = output_element.scrollHeight

        return result

    # 출력이 터미널로 나오게 stdout을 변조시키기 위한 클래스
    class TerminalOutputStream:
        def __init__(self, is_error=False):
            self.is_error = is_error
            self.buffer = []

        def write(self, text):
            if text:
                append_to_terminal(text, scroll=True)
                self.buffer.append(text)

        def flush(self):
            pass

        def getvalue(self):
            return "".join(self.buffer)

    # 코드 실행
    async def run_code(event):
        code = view.state.doc.toString()

        redirected_output = TerminalOutputStream()
        redirected_error = TerminalOutputStream(is_error=True)

        sys.stdout = redirected_output
        sys.stderr = redirected_error

        status_element.textContent = "실행 중..."
        status_element.style.color = "#ff9800"

        output_element.innerHTML = ""

        start_time = time.time()

        try:
            import builtins
            import re

            old_input = builtins.input
            builtins.input = custom_input

            # 실시간으로 입력을 받기 위해 입력이 비동기적으로 이루어져야 하기에, input(...)을 (await input(...))로 변환하기 위한 함수
            def transform_input_calls(code):
                result = []
                i = 0
                while i < len(code):
                    match = re.search(r"\binput\s*\(", code[i:])
                    if not match:
                        result.append(code[i:])
                        break

                    result.append(code[i : i + match.start()])

                    result.append("(await input(")

                    paren_start = i + match.end()

                    paren_count = 1
                    j = paren_start
                    in_string = False
                    string_char = None

                    while j < len(code) and paren_count > 0:
                        char = code[j]

                        if char in ['"', "'"]:
                            if not in_string:
                                in_string = True
                                string_char = char
                            elif char == string_char and (
                                j == 0 or code[j - 1] != "\\"
                            ):
                                in_string = False
                                string_char = None

                        elif not in_string:
                            if char == "(":
                                paren_count += 1
                            elif char == ")":
                                paren_count -= 1

                        j += 1

                    result.append(code[paren_start : j - 1])

                    result.append("))")

                    i = j

                return "".join(result)

            transformed_code = transform_input_calls(code)

            if transformed_code.strip() == "":
                transformed_code = "pass"

            indented_code = "\n".join(
                "    " + line for line in transformed_code.split("\n")
            )
            wrapped_code = f"""async def __user_main__():
{indented_code}
"""

            # js를 임포트할 경우 XSS 공격 등이 가능하기에, 이를 차단하기 위해 제한된 input 함수
            def restricted_import(name, *args, **kwargs):
                if name == "js" or name.startswith("js."):
                    raise ImportError(
                        "보안상의 이유로 'js' 모듈을 임포트할 수 없습니다."
                    )
                elif name == "pyodide" or name.startswith("pyodide."):
                    raise ImportError(
                        "보안상의 이유로 'pyodide' 모듈을 임포트할 수 없습니다."
                    )
                elif name == "pyodide_js" or name.startswith("pyodide_js."):
                    raise ImportError(
                        "보안상의 이유로 'pyodide_js' 모듈을 임포트할 수 없습니다."
                    )
                return __import__(name, *args, **kwargs)

            import types

            restricted_builtins = types.ModuleType("builtins")
            for attr in dir(builtins):
                if attr == "__import__":
                    setattr(restricted_builtins, attr, restricted_import)
                else:
                    setattr(restricted_builtins, attr, getattr(builtins, attr))

            import sys as original_sys

            removed_modules = {}
            for mod_name in list(original_sys.modules.keys()):
                if (
                    mod_name == "js"
                    or mod_name.startswith("js.")
                    or mod_name == "pyodide"
                    or mod_name.startswith("pyodide.")
                    or mod_name == "pyodide_js"
                    or mod_name.startswith("pyodide_js.")
                ):
                    removed_modules[mod_name] = original_sys.modules.pop(mod_name)

            exec_globals = {
                "__name__": "__main__",
                "__builtins__": restricted_builtins,
            }

            exec(wrapped_code, exec_globals)

            await exec_globals["__user_main__"]()

            stdout_value = redirected_output.getvalue()
            stderr_value = redirected_error.getvalue()

            if not stdout_value and not stderr_value:
                append_to_terminal("(출력 없음)\n", scroll=True)

            elapsed = time.time() - start_time
            status_element.textContent = "실행 완료"
            status_element.style.color = "#4CAF50"
            exec_time_element.textContent = f"{elapsed:.3f}초"

            builtins.input = old_input

        except Exception:
            append_to_terminal("=== 에러 발생 ===\n", scroll=True)
            append_to_terminal(traceback.format_exc() + "\n", scroll=True)

            status_element.textContent = "에러 발생"
            status_element.style.color = "#f44336"
            exec_time_element.textContent = ""

            global current_input_element
            if current_input_element:
                try:
                    output_element.removeChild(current_input_element)
                    current_input_element = None
                except Exception:
                    pass

    # 초기화 버튼 처리를 위한 함수
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

    # 출력 지우기 버튼 처리를 위한 함수
    def clear_output(event):
        global current_input_element
        output_element.innerHTML = ""
        status_element.textContent = "준비"
        status_element.style.color = "#5f6368"
        exec_time_element.textContent = ""
        current_input_element = None

    # 패키지 설치 버튼 처리를 위한 함수
    async def install_package(event):
        package_input = document.getElementById("packageInput")
        package_name = package_input.value.strip()

        if not package_name:
            status_element.textContent = "패키지 이름을 입력하세요"
            status_element.style.color = "#f44336"
            return

        status_element.textContent = f"{package_name} 설치 중..."
        status_element.style.color = "#ff9800"

        try:
            import micropip

            await micropip.install(package_name)

            status_element.textContent = f"{package_name} 설치 완료"
            status_element.style.color = "#4CAF50"

            package_input.value = ""

            async def reset_status():
                await asyncio.sleep(2)
                status_element.textContent = "준비"
                status_element.style.color = "#5f6368"

            asyncio.create_task(reset_status())

        except Exception as e:
            status_element.textContent = f"설치 실패: {str(e)}"
            status_element.style.color = "#f44336"

    run_btn = document.getElementById("runBtn")
    clear_btn = document.getElementById("clearBtn")
    clear_output_btn = document.getElementById("clearOutputBtn")
    install_btn = document.getElementById("installBtn")

    run_btn.addEventListener("click", create_proxy(run_code))
    clear_btn.addEventListener("click", create_proxy(clear_editor))
    clear_output_btn.addEventListener("click", create_proxy(clear_output))
    install_btn.addEventListener("click", create_proxy(install_package))

    # 파이썬 환경 세팅이 완전히 마무리되면 실행될 명령들
    loading_element.classList.add("hidden")

    status_element.textContent = "준비 완료"
    status_element.style.color = "#4CAF50"

    async def show_ready():
        await asyncio.sleep(1)
        status_element.textContent = "준비"
        status_element.style.color = "#5f6368"

    asyncio.create_task(show_ready())
