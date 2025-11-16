import webbrowser

try:
    from bottle import route, run, template
except ImportError:
    import pip

    pip.main(["install", "bottle"])
    from bottle import route, run, template


@route("/")
def main():
    return template(
        "index.html",
        init=r'''
import micropip
await micropip.install("jedi")
import jedi
from js import console, document, window
from pyodide.ffi import create_proxy, to_js
import asyncio

EditorView = window.EditorView
basicSetup = window.basicSetup
python_lang = window.python_lang
autocompletion = window.autocompletion
linter = window.linter

def get_line_col(text, offset):
    line = 1
    col = 0
    for i in range(min(offset, len(text))):
        if text[i] == "\\n":
            line += 1
            col = 0
        else:
            col += 1
    return line, col

def pos_to_offset(text, line, col):
    lines = text.split("\\n")
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
        result.append({
            'label': completion.name,
            'type': completion.type,
            'info': completion.docstring(raw=True)[:200] if completion.docstring(raw=True) else ''
        })
    return result

def get_diagnostics(code):
    errors = []
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        errors.append({
            'line': (e.lineno - 1) if e.lineno else 0,
            'col': (e.offset - 1) if e.offset else 0,
            'message': str(e.msg),
            'severity': 'error'
        })
    except Exception as e:
        errors.append({
            'line': 0,
            'col': 0,
            'message': str(e),
            'severity': 'error'
        })
    return errors

def python_completions_handler(context):
    code = context.state.doc.toString()
    pos = context.pos

    word_start = pos
    while word_start > 0:
        char = code[word_start - 1]
        if not (char.isalnum() or char == '_'):
            break
        word_start -= 1

    completions = get_completions(code, pos)

    if not completions:
        return None

    options = []
    for c in completions:
        options.append(to_js({
            'label': c['label'],
            'type': c['type'],
            'info': c['info']
        }))

    return to_js({
        'from': word_start,
        'to': pos,
        'options': to_js(options)
    })

def python_linter_handler(view):
    code = view.state.doc.toString()
    diagnostics = get_diagnostics(code)

    result = []
    for d in diagnostics:
        offset_from = pos_to_offset(code, d['line'], d['col'])
        offset_to = pos_to_offset(code, d['line'], d['col'] + 1)

        result.append(to_js({
            'from': offset_from,
            'to': offset_to,
            'severity': d['severity'],
            'message': d['message']
        }))

    return to_js(result)

completions_proxy = create_proxy(python_completions_handler)
linter_proxy = create_proxy(python_linter_handler)

initial_code = """import math

def calculate(x):
    return math.sqrt(x)

print(calculate(16))
"""

extensions = to_js([
    basicSetup,
    python_lang(),
    autocompletion(to_js({
        'override': to_js([completions_proxy])
    })),
    linter(linter_proxy, to_js({'delay': 500}))
])

view = EditorView.new(to_js({
    'doc': initial_code,
    'parent': document.body,
    'extensions': extensions
}))

async def show_status():
    status = document.createElement('div')
    status.style.cssText = 'position: fixed; top: 10px; right: 10px; padding: 10px; background: #4CAF50; color: white; border-radius: 5px; z-index: 1000;'
    status.textContent = '에디터 초기화 완료'
    document.body.appendChild(status)

    await asyncio.sleep(3)
    status.remove()

asyncio.create_task(show_status())
        ''',
    )


if __name__ == "__main__":
    webbrowser.open("http://localhost:3000")
    run(host="localhost", port=3000, debug=True)
