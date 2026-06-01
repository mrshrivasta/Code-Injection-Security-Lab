#!/usr/bin/env python3
"""
Code Injection Demo — Educational Tool
Made by Karanam Shrivasta
LinkedIn: linkedin.com/in/karanam-shrivasta
GitHub  : github.com/mrshrivasta

HOW TO RUN:
  pip install flask
  python code_injection_demo.py
  Open http://localhost:5000

⚠ EDUCATIONAL USE ONLY
All demos run in a sandboxed local environment.
No real system is harmed. Never use these techniques
on real applications without explicit permission.
May violate CFAA (US), CMA 1990 (UK), IT Act 2000 (India).
"""

import sys, json, re, html, subprocess, platform, textwrap
from flask import Flask, jsonify, request

app = Flask(__name__)
OS = platform.system()

# ══════════════════════════════════════════════════════════
# SANDBOXED VULNERABLE FUNCTIONS
# All run on local in-memory data only
# ══════════════════════════════════════════════════════════

# ── 1. eval() injection ───────────────────────────────────
SAFE_CALC_HISTORY = []

def vuln_eval(expr):
    """Vulnerable: passes user input directly to eval()"""
    try:
        result = eval(expr)
        return {"result": str(result), "expr": expr, "method": "eval()", "error": None}
    except Exception as e:
        return {"result": None, "expr": expr, "method": "eval()", "error": str(e)}

def safe_calc(expr):
    """Safe: only allows digits and math operators"""
    if not re.fullmatch(r"[\d\s\+\-\*\/\.\(\)]+", expr):
        return {"result": None, "expr": expr, "method": "whitelist regex",
                "error": "Rejected: expression contains non-math characters"}
    try:
        result = eval(compile(expr, "<string>", "eval"))
        return {"result": str(result), "expr": expr, "method": "whitelisted eval", "error": None}
    except Exception as e:
        return {"result": None, "expr": expr, "method": "whitelist regex", "error": str(e)}

# ── 2. exec() injection ───────────────────────────────────
def vuln_exec(code):
    """Vulnerable: executes arbitrary Python via exec()"""
    output_capture = []
    sandbox_globals = {
        "__builtins__": {"print": lambda *a: output_capture.append(" ".join(str(x) for x in a)),
                         "range": range, "len": len, "str": str, "int": int,
                         "list": list, "dict": dict, "sum": sum, "max": max, "min": min},
        "__output__": output_capture,
    }
    try:
        exec(compile(code, "<sandbox>", "exec"), sandbox_globals)
        return {"output": "\n".join(output_capture) or "(no output)",
                "code": code, "error": None}
    except Exception as e:
        return {"output": "\n".join(output_capture), "code": code, "error": str(e)}

def safe_exec(code):
    """Safe: restricted AST check + sandboxed builtins — blocks imports, file ops, etc."""
    import ast
    FORBIDDEN = {"Import", "ImportFrom", "Call"}
    FORBIDDEN_NAMES = {"open","__import__","exec","eval","compile","globals",
                       "locals","getattr","setattr","delattr","vars","dir",
                       "os","sys","subprocess","socket","requests"}
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"output": None, "code": code, "error": f"SyntaxError: {e}"}
    for node in ast.walk(tree):
        if type(node).__name__ in FORBIDDEN:
            return {"output": None, "code": code,
                    "error": f"Blocked: {type(node).__name__} is not allowed in safe mode"}
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            return {"output": None, "code": code,
                    "error": f"Blocked: '{node.id}' is a forbidden identifier"}
    return vuln_exec(code)

# ── 3. template injection (SSTI) ─────────────────────────
def vuln_template(name, template):
    """Vulnerable: user controls the template string"""
    try:
        from string import Formatter
        result = template.format(name=name, greeting="Hello")
        return {"rendered": result, "template": template, "error": None}
    except Exception as e:
        return {"rendered": None, "template": template, "error": str(e)}

def safe_template(name, template):
    """Safe: only allows {name} and {greeting} placeholders"""
    allowed = re.compile(r"^\{(name|greeting)\}$")
    placeholders = re.findall(r"\{[^}]*\}", template)
    for p in placeholders:
        if not allowed.match(p):
            return {"rendered": None, "template": template,
                    "error": f"Blocked placeholder: {p} — only {{name}} and {{greeting}} allowed"}
    try:
        result = template.format(name=html.escape(name), greeting="Hello")
        return {"rendered": result, "template": template, "error": None}
    except Exception as e:
        return {"rendered": None, "template": template, "error": str(e)}

# ── 4. OS command injection ───────────────────────────────
FAKE_FILES = ["report.txt", "data.csv", "notes.md", "config.json", "readme.txt"]

def vuln_cmd(filename):
    """Vulnerable: concatenates user input into shell command"""
    # We simulate the command — never actually execute shell with user input
    fake_cmd = f"cat /uploads/{filename}"
    # Detect injection patterns
    injections = []
    if ";" in filename: injections.append(f"Semicolon chain: cat ... ; <injected>")
    if "&&" in filename: injections.append(f"AND chain: cat ... && <injected>")
    if "|" in filename: injections.append(f"Pipe injection: cat ... | <injected>")
    if "`" in filename: injections.append(f"Backtick execution: `<injected>`")
    if "$(" in filename: injections.append(f"Command substitution: $(<injected>)")
    if ">" in filename or ">>" in filename: injections.append("Redirect: output to file")
    if "&" in filename and "&&" not in filename: injections.append("Background job: &<injected>")

    if injections:
        return {"cmd": fake_cmd, "injected": True, "injections": injections,
                "output": f"[SIMULATED] Would execute injected commands:\n" +
                          "\n".join(f"  → {i}" for i in injections),
                "error": None}
    if filename in FAKE_FILES:
        fake_contents = {
            "report.txt": "Q3 Sales Report\nRevenue: $1,240,000\nGrowth: 12%",
            "data.csv": "id,name,value\n1,alpha,100\n2,beta,200",
            "notes.md": "# Notes\n- Fix login bug\n- Deploy v2.1",
            "config.json": '{"debug": false, "version": "2.1.0"}',
            "readme.txt": "Welcome to the demo application.",
        }
        return {"cmd": fake_cmd, "injected": False, "injections": [],
                "output": fake_contents.get(filename, "File found."), "error": None}
    return {"cmd": fake_cmd, "injected": False, "injections": [],
            "output": f"cat: /uploads/{filename}: No such file", "error": None}

def safe_cmd(filename):
    """Safe: whitelist validation — only alphanumeric + . and -"""
    if not re.fullmatch(r"[\w\-\.]+", filename) or ".." in filename:
        return {"cmd": "REJECTED", "injected": False, "injections": [],
                "output": None,
                "error": f"Input rejected: '{filename}' contains illegal characters"}
    return {"cmd": f"cat /uploads/{filename}", "injected": False, "injections": [],
            "output": "Input validated — safe to use.", "error": None}

# ── 5. pickle deserialization ─────────────────────────────
import pickle, base64

class SafeUser:
    def __init__(self, name, role):
        self.name = name
        self.role = role

def make_safe_pickle():
    u = SafeUser("alice", "viewer")
    return base64.b64encode(pickle.dumps(u)).decode()

def make_malicious_pickle():
    """Creates a pickle that would execute code when deserialized."""
    class Exploit:
        def __reduce__(self):
            # In real attack: os.system("malicious command")
            # Here we just demonstrate the structure — no real execution
            return (print, ("⚠ Pickle RCE payload executed during deserialization!",))
    return base64.b64encode(pickle.dumps(Exploit())).decode()

def vuln_deserialize(b64_data):
    """Vulnerable: blindly deserializes user-supplied pickle"""
    output_log = []
    try:
        raw = base64.b64decode(b64_data)
        # intercept print to capture output
        import io
        import builtins
        captured = []
        orig_print = builtins.print
        builtins.print = lambda *a,**kw: captured.append(" ".join(str(x) for x in a))
        obj = pickle.loads(raw)
        builtins.print = orig_print
        return {
            "success": True,
            "object_type": type(obj).__name__,
            "output": captured[0] if captured else str(obj),
            "error": None,
            "dangerous": len(captured) > 0,
        }
    except Exception as e:
        return {"success": False, "object_type": None, "output": None,
                "error": str(e), "dangerous": False}

def safe_deserialize(b64_data):
    """Safe: uses JSON instead of pickle"""
    try:
        raw = base64.b64decode(b64_data).decode()
        obj = json.loads(raw)
        return {"success": True, "object_type": type(obj).__name__,
                "output": str(obj), "error": None}
    except Exception as e:
        return {"success": False, "output": None, "error": str(e)}

def make_safe_json():
    return base64.b64encode(json.dumps({"name": "alice", "role": "viewer"}).encode()).decode()

# ── 6. format string injection ────────────────────────────
SECRET_CONFIG = {"db_password": "Sup3rS3cr3t!", "api_key": "sk-abc123",
                 "admin_token": "tok_xyz789", "internal_ip": "10.0.0.1"}

def vuln_format(template):
    """Vulnerable: user controls format string with access to globals"""
    try:
        result = template.format(**SECRET_CONFIG)
        return {"rendered": result, "template": template, "error": None, "leaked": True}
    except KeyError as e:
        return {"rendered": None, "template": template,
                "error": f"KeyError: {e} — variable not found", "leaked": False}
    except Exception as e:
        return {"rendered": None, "template": template, "error": str(e), "leaked": False}

def safe_format(template, name):
    """Safe: only user-controlled safe variables, no internal config access"""
    try:
        result = template.format(name=html.escape(name), app="DemoApp")
        return {"rendered": result, "template": template, "error": None, "leaked": False}
    except KeyError as e:
        return {"rendered": None, "template": template,
                "error": f"Unknown variable: {e}. Only {{name}} and {{app}} are allowed.",
                "leaked": False}
    except Exception as e:
        return {"rendered": None, "template": template, "error": str(e), "leaked": False}

# ══════════════════════════════════════════════════════════
# PAYLOADS LIBRARY
# ══════════════════════════════════════════════════════════
PAYLOADS = {
    "eval": [
        {"label": "Math (safe)", "payload": "2 + 2 * 10",
         "desc": "Normal calculator input", "expect": "safe"},
        {"label": "__import__ os", "payload": "__import__('os').getcwd()",
         "desc": "Import os module to read working directory", "expect": "dangerous"},
        {"label": "List files", "payload": "__import__('os').listdir('.')",
         "desc": "List files in current directory", "expect": "dangerous"},
        {"label": "Read file", "payload": "open('README.md').read() if __import__('os').path.exists('README.md') else 'no file'",
         "desc": "Read a file from the filesystem", "expect": "dangerous"},
        {"label": "System info", "payload": "__import__('platform').uname()",
         "desc": "Leak system information", "expect": "dangerous"},
    ],
    "exec": [
        {"label": "Hello world (safe)", "payload": "print('Hello, World!')",
         "desc": "Simple print statement", "expect": "safe"},
        {"label": "Loop (safe)", "payload": "for i in range(3):\n    print(f'Line {i}')",
         "desc": "Loop with print", "expect": "safe"},
        {"label": "Import os (blocked)", "payload": "import os\nprint(os.getcwd())",
         "desc": "Attempt to import os module", "expect": "blocked"},
        {"label": "Open file (blocked)", "payload": "open('secret.txt', 'w').write('hacked')",
         "desc": "Attempt file write operation", "expect": "blocked"},
    ],
    "cmd": [
        {"label": "Normal file", "payload": "report.txt",
         "desc": "Normal filename — safe", "expect": "safe"},
        {"label": "Semicolon chain", "payload": "report.txt; cat /etc/passwd",
         "desc": "Chain a second command with ;", "expect": "dangerous"},
        {"label": "AND chain", "payload": "report.txt && whoami",
         "desc": "Run second command if first succeeds", "expect": "dangerous"},
        {"label": "Pipe injection", "payload": "report.txt | id",
         "desc": "Pipe output to another command", "expect": "dangerous"},
        {"label": "Backtick RCE", "payload": "`whoami`",
         "desc": "Execute command via backtick substitution", "expect": "dangerous"},
        {"label": "Path traversal", "payload": "../../etc/passwd",
         "desc": "Traverse up the directory tree", "expect": "dangerous"},
    ],
    "ssti": [
        {"label": "Normal greeting", "payload": "Hello {name}!",
         "desc": "Normal template usage", "expect": "safe"},
        {"label": "Config access", "payload": "{name.__class__.__mro__}",
         "desc": "Access class internals via template", "expect": "dangerous"},
        {"label": "Globals leak", "payload": "{greeting.__class__.__init__.__globals__}",
         "desc": "Leak Python globals through template", "expect": "dangerous"},
    ],
    "format": [
        {"label": "Normal", "payload": "Welcome {name}!",
         "desc": "Normal format string — safe", "expect": "safe"},
        {"label": "Leak db_password", "payload": "DB pass: {db_password}",
         "desc": "Access secret variable by name", "expect": "dangerous"},
        {"label": "Leak api_key", "payload": "Key: {api_key}",
         "desc": "Leak API key from internal config", "expect": "dangerous"},
        {"label": "Leak all secrets", "payload": "All: {db_password} / {api_key} / {admin_token}",
         "desc": "Dump multiple secrets at once", "expect": "dangerous"},
    ],
}

# ══════════════════════════════════════════════════════════
# FLASK ROUTES
# ══════════════════════════════════════════════════════════
@app.route("/")
def index(): return HTML

@app.route("/api/payloads")
def api_payloads(): return jsonify(PAYLOADS)

@app.route("/api/eval", methods=["POST"])
def api_eval():
    d = request.get_json()
    mode = d.get("mode","vuln")
    expr = d.get("expr","1+1")[:500]
    if mode == "safe":
        return jsonify(safe_calc(expr))
    return jsonify(vuln_eval(expr))

@app.route("/api/exec", methods=["POST"])
def api_exec():
    d = request.get_json()
    mode = d.get("mode","vuln")
    code = d.get("code","print('hi')")[:1000]
    if mode == "safe":
        return jsonify(safe_exec(code))
    return jsonify(vuln_exec(code))

@app.route("/api/cmd", methods=["POST"])
def api_cmd():
    d = request.get_json()
    mode = d.get("mode","vuln")
    filename = d.get("filename","report.txt")[:200]
    if mode == "safe":
        return jsonify(safe_cmd(filename))
    return jsonify(vuln_cmd(filename))

@app.route("/api/template", methods=["POST"])
def api_template():
    d = request.get_json()
    mode = d.get("mode","vuln")
    name = d.get("name","Alice")[:100]
    template = d.get("template","Hello {name}")[:500]
    if mode == "safe":
        return jsonify(safe_template(name, template))
    return jsonify(vuln_template(name, template))

@app.route("/api/format", methods=["POST"])
def api_format():
    d = request.get_json()
    mode = d.get("mode","vuln")
    template = d.get("template","Hello {name}")[:500]
    name = d.get("name","Alice")[:100]
    if mode == "safe":
        return jsonify(safe_format(template, name))
    return jsonify(vuln_format(template))

@app.route("/api/pickle", methods=["POST"])
def api_pickle():
    d = request.get_json()
    action = d.get("action","safe_payload")
    if action == "make_safe":
        return jsonify({"payload": make_safe_pickle(), "type": "SafeUser object"})
    if action == "make_malicious":
        return jsonify({"payload": make_malicious_pickle(), "type": "Malicious RCE payload"})
    if action == "make_json":
        return jsonify({"payload": make_safe_json(), "type": "JSON (safe alternative)"})
    # deserialize
    mode = d.get("mode","vuln")
    payload = d.get("payload","")
    if mode == "safe":
        return jsonify(safe_deserialize(payload))
    return jsonify(vuln_deserialize(payload))

# ══════════════════════════════════════════════════════════
# HTML
# ══════════════════════════════════════════════════════════
HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#0D1117">
<title>Code Injection Demo | Karanam Shrivasta</title>
<meta name="description" content="Educational code injection demo — eval, exec, command injection, SSTI, pickle, format string. By Karanam Shrivasta.">
<meta name="keywords" content="code injection, eval injection, command injection, SSTI, pickle deserialization, format string, security education, Karanam Shrivasta">
<meta name="author" content="Karanam Shrivasta">
<meta name="robots" content="index,follow">
<meta name="geo.region" content="IN">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"SoftwareApplication","name":"Code Injection Demo","applicationCategory":"SecurityApplication","author":{"@type":"Person","name":"Karanam Shrivasta","url":"https://www.linkedin.com/in/karanam-shrivasta/","sameAs":["https://github.com/mrshrivasta"]},"offers":{"@type":"Offer","price":"0"}}</script>
<style>
:root{--bg:#0D1117;--bg2:#161B22;--bg3:#1C2128;--card:#21262D;--bdr:#30363D;--text:#E6EDF3;--muted:#8B949E;--blue:#58A6FF;--green:#3FB950;--red:#F85149;--amber:#D29922;--purple:#BC8CFF;--cyan:#39C5BB;--nav:56px;--bot:60px;--sat:env(safe-area-inset-top,0px);--sab:env(safe-area-inset-bottom,0px)}
[data-theme="light"]{--bg:#F6F8FA;--bg2:#fff;--bg3:#F1F3F5;--card:#fff;--bdr:#D0D7DE;--text:#1F2328;--muted:#636C76}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html,body{height:100%;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);font-size:13px;padding-top:calc(var(--nav) + var(--sat))}
/* nav */
.tnav{position:fixed;top:0;left:0;right:0;z-index:200;background:var(--bg2);border-bottom:1px solid var(--bdr);height:calc(var(--nav) + var(--sat));padding-top:var(--sat);display:flex;align-items:center;justify-content:space-between;padding-left:1rem;padding-right:1rem}
.brand{font-size:14px;font-weight:700;display:flex;align-items:center;gap:6px}
/* main */
.main{height:100%;overflow-y:auto;overflow-x:hidden;padding-bottom:calc(var(--bot) + var(--sab) + 1rem);-webkit-overflow-scrolling:touch}
.page{display:none;padding:1rem}.page.on{display:block}
/* bottom bar */
.bbar{position:fixed;bottom:0;left:0;right:0;z-index:200;background:var(--bg2);border-top:1px solid var(--bdr);height:calc(var(--bot) + var(--sab));padding-bottom:var(--sab);display:flex;overflow-x:auto;scrollbar-width:none}
.bbar::-webkit-scrollbar{display:none}
.btab{flex:1;min-width:54px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;border:none;background:none;color:var(--muted);cursor:pointer;padding:6px 2px;font-size:9px;transition:color .15s}
.btab.on{color:var(--blue)}.btab:active{opacity:.7}
.btab .ico{font-size:18px;line-height:1}.btab .lbl{font-size:9px;font-weight:500;white-space:nowrap;max-width:54px;overflow:hidden;text-overflow:ellipsis}
/* cards */
.card{background:var(--card);border:1px solid var(--bdr);border-radius:12px;padding:1rem;margin-bottom:.75rem}
.ct{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:.75rem}
/* disc */
.disc{background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:.875rem 1rem;margin-bottom:.875rem}
.disc h3{font-size:12px;font-weight:700;color:#991B1B;margin-bottom:4px}.disc p{font-size:12px;color:#B91C1C;line-height:1.7}
/* code editor */
.code-editor{background:#010409;border:1px solid var(--bdr);border-radius:10px;padding:.875rem;font-family:'Courier New',monospace;font-size:12px;color:#E6EDF3;width:100%;min-height:80px;resize:vertical;line-height:1.8;outline:none;caret-color:var(--blue)}
.code-editor:focus{border-color:var(--blue)}
textarea{border:1px solid var(--bdr);border-radius:10px;padding:.875rem;font-family:'Courier New',monospace;font-size:12px;background:#010409;color:#E6EDF3;width:100%;resize:vertical;line-height:1.8;outline:none;caret-color:var(--blue)}
textarea:focus{border-color:var(--blue)}
input[type=text]{border:1px solid var(--bdr);border-radius:8px;padding:9px 12px;font-size:13px;background:var(--bg3);color:var(--text);width:100%;font-family:inherit}
input[type=text]:focus{outline:2px solid var(--blue);border-color:transparent}
/* mode toggle */
.mode-row{display:flex;gap:6px;margin-bottom:.875rem}
.mode-btn{flex:1;padding:9px;border-radius:8px;border:1px solid var(--bdr);font-size:12px;font-weight:600;cursor:pointer;background:var(--bg3);color:var(--muted);transition:all .15s;font-family:inherit;text-align:center}
.mode-btn.vuln.on{background:rgba(248,81,73,.15);color:var(--red);border-color:rgba(248,81,73,.4)}
.mode-btn.safe.on{background:rgba(63,185,80,.15);color:var(--green);border-color:rgba(63,185,80,.4)}
/* result box */
.result-box{border-radius:10px;padding:.875rem;margin-top:.75rem;font-family:'Courier New',monospace;font-size:11px;line-height:1.8;white-space:pre-wrap;word-break:break-all;display:none;border:1px solid var(--bdr)}
.result-box.danger{background:rgba(248,81,73,.07);border-color:rgba(248,81,73,.3);color:#F85149}
.result-box.safe-res{background:rgba(63,185,80,.07);border-color:rgba(63,185,80,.3);color:#3FB950}
.result-box.blocked{background:rgba(88,166,255,.07);border-color:rgba(88,166,255,.3);color:#58A6FF}
.result-box.normal{background:var(--bg3);color:var(--text)}
/* query highlight */
.query-box{background:#010409;border:1px solid var(--bdr);border-radius:8px;padding:.875rem;font-family:'Courier New',monospace;font-size:11px;line-height:1.8;overflow-x:auto;white-space:pre-wrap;word-break:break-all;color:#8B949E;margin:.75rem 0}
/* explain */
.explain{background:rgba(88,166,255,.07);border-left:3px solid var(--blue);border-radius:0 8px 8px 0;padding:.75rem .875rem;font-size:12px;color:var(--muted);line-height:1.7;margin-top:.75rem}
/* payload chips */
.chip-row{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:.875rem}
.chip{padding:5px 10px;border-radius:6px;border:1px solid var(--bdr);font-size:11px;cursor:pointer;background:var(--bg3);color:var(--text);transition:all .12s;font-family:'Courier New',monospace}
.chip:hover{border-color:var(--blue);color:var(--blue)}
.chip.danger{border-color:rgba(248,81,73,.3);color:var(--red)}
.chip.safe-c{border-color:rgba(63,185,80,.3);color:var(--green)}
/* btn */
.btn{padding:11px 18px;border-radius:10px;border:none;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;display:inline-flex;align-items:center;gap:6px;transition:opacity .15s}
.btn:active{opacity:.75}.bl{background:var(--blue);color:#fff}.br{background:var(--red);color:#fff}.bgr{background:var(--green);color:#000}.bgray{background:var(--bg3);color:var(--text);border:1px solid var(--bdr)}
.btn-full{width:100%;justify-content:center}
/* compare */
.compare{
  display:grid;
  grid-template-columns:minmax(0,1fr) minmax(0,1fr);
  gap:.75rem;
}

.compare > *{
  min-width:0;
}
.vuln-side{border:1px solid rgba(248,81,73,.3);border-radius:10px;padding:.875rem}
.safe-side{border:1px solid rgba(63,185,80,.3);border-radius:10px;padding:.875rem}
.side-title{font-size:12px;font-weight:700;margin-bottom:.75rem}
.vuln-side .side-title{color:var(--red)}.safe-side .side-title{color:var(--green)}
/* code block */
.codeblock{
  background:#010409;
  border:1px solid var(--bdr);
  border-radius:8px;
  padding:.875rem;
  font-family:'Courier New', monospace;
  font-size:10px;
  line-height:1.6;
  white-space:pre-wrap;
  word-break:break-word;
  overflow-wrap:anywhere;
  overflow:hidden;
  max-width:100%;
}
  background:#010409;
  border:1px solid var(--bdr);
  border-radius:8px;
  padding:.875rem;
  font-family:'Courier New',monospace;
  font-size:11px;
  line-height:1.8;
  overflow-x:auto;
  white-space:pre;
}
/* badge */
.bd{display:inline-block;padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700}
.b-ok{background:rgba(63,185,80,.15);color:var(--green)}.b-er{background:rgba(248,81,73,.15);color:var(--red)}.b-bl{background:rgba(88,166,255,.12);color:var(--blue)}.b-wn{background:rgba(210,153,34,.15);color:var(--amber)}
/* overview cards */
.ov-card{background:var(--card);border:1px solid var(--bdr);border-radius:12px;padding:1rem;cursor:pointer;transition:border-color .15s;margin-bottom:.625rem;display:flex;align-items:center;gap:10px}
.ov-card:hover,.ov-card:active{border-color:var(--blue);opacity:.9}
.ov-icon{font-size:28px;flex-shrink:0}
/* wm */
.wm{text-align:center;padding:1.5rem 1rem;border-top:1px solid var(--bdr);margin-top:1rem}
.wm .n{font-size:13px;font-weight:700;margin-bottom:4px}.wm .r{font-size:11px;color:var(--muted);margin-bottom:8px}
.wm a{font-size:12px;color:var(--blue);text-decoration:none;margin:0 6px;font-weight:600}
.spin{display:inline-block;width:12px;height:12px;border:2px solid var(--bdr);border-top-color:var(--blue);border-radius:50%;animation:sp .5s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
@media(min-width:600px){
  .tnav,
  .bbar,
  .main{
    max-width:640px;
    margin:0 auto;
    left:0;
    right:0;
    transform:none;
  }
  .tnav,
  .bbar{
    border-left:1px solid var(--bdr);
    border-right:1px solid var(--bdr);
  }
  .compare{
    grid-template-columns:1fr 1fr;
  }
}
@media(max-width:480px){.compare{grid-template-columns:1fr}}
</style>
</head>
<body>

<div class="tnav">
  <div class="brand">💉 Code Injection Demo</div>
  <div style="display:flex;gap:6px;align-items:center">
    <span style="font-size:10px;background:rgba(248,81,73,.15);color:var(--red);border:1px solid rgba(248,81,73,.3);border-radius:5px;padding:3px 7px">LOCAL ONLY</span>
    <button onclick="toggleTheme()" style="background:none;border:none;cursor:pointer;font-size:18px;color:var(--muted)" id="theme-btn">🌙</button>
  </div>
</div>

<div class="main" id="scroll">

<!-- ══ OVERVIEW ══ -->
<div id="p-overview" class="page on">
  <div class="disc">
    <h3>⚠️ Educational use only — local sandbox</h3>
    <p>All demos run in a <strong>sandboxed local environment</strong>. No real system is harmed. Never use these techniques on real applications without explicit written permission. May violate CFAA (US), CMA 1990 (UK), IT Act 2000 (India). <strong>Karanam Shrivasta</strong> assumes zero liability.</p>
  </div>
  <div style="font-size:13px;color:var(--muted);margin-bottom:1rem;line-height:1.7">
    Code injection occurs when an attacker inserts malicious code into a vulnerable application that then executes it. It is a root cause of many critical CVEs and consistently appears in the OWASP Top 10.
  </div>
  <div id="ov-cards"></div>
</div>

<!-- ══ EVAL INJECTION ══ -->
<div id="p-eval" class="page">
  <div class="card">
    <div class="ct">eval() injection — calculator</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:.875rem">The app passes user input directly to Python's <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">eval()</code>. This allows execution of arbitrary Python expressions.</p>
    <div class="mode-row">
      <button class="mode-btn vuln on" id="eval-vuln-btn" onclick="setMode('eval','vuln')">❌ Vulnerable</button>
      <button class="mode-btn safe" id="eval-safe-btn" onclick="setMode('eval','safe')">✅ Secure</button>
    </div>
    <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:5px">Expression</label>
    <input type="text" id="eval-input" value="2 + 2" placeholder="Enter expression...">
    <div class="ct" style="margin-top:.875rem;margin-bottom:6px">Quick payloads</div>
    <div class="chip-row" id="eval-chips"></div>
    <button class="btn bl btn-full" style="margin-top:.5rem" onclick="runEval()">▶ Execute</button>
  </div>
  <div id="eval-result" class="result-box"></div>
  <div class="explain" id="eval-explain" style="display:none"></div>
  <div class="card" style="margin-top:.75rem">
    <div class="ct">Code comparison</div>
    <div class="compare">
      <div class="vuln-side">
        <div class="side-title">❌ Vulnerable</div>
        <div class="codeblock"><span style="color:#F85149">result = eval(user_input)
# user_input = "__import__('os').listdir('.')"
# → lists your files!</span></div>
      </div>
      <div class="safe-side">
        <div class="side-title">✅ Secure</div>
        <div class="codeblock"><span style="color:#3FB950">import re
pattern = r'^[\d\s\+\-\*\/\.\(\)]+$'
if re.fullmatch(pattern, expr):
    result = eval(expr)
else:
    raise ValueError("Invalid")</span></div>
      </div>
    </div>
  </div>
</div>

<!-- ══ EXEC INJECTION ══ -->
<div id="p-exec" class="page">
  <div class="card">
    <div class="ct">exec() injection — code runner</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:.875rem">An online code runner that uses <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">exec()</code>. Vulnerable version allows imports and file operations. Secure version restricts via AST analysis.</p>
    <div class="mode-row">
      <button class="mode-btn vuln on" id="exec-vuln-btn" onclick="setMode('exec','vuln')">❌ Vulnerable</button>
      <button class="mode-btn safe" id="exec-safe-btn" onclick="setMode('exec','safe')">✅ Secure</button>
    </div>
    <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:5px">Python code</label>
    <textarea id="exec-input" rows="5" placeholder="print('hello')">print('Hello, World!')</textarea>
    <div class="ct" style="margin-top:.875rem;margin-bottom:6px">Quick payloads</div>
    <div class="chip-row" id="exec-chips"></div>
    <button class="btn bl btn-full" style="margin-top:.5rem" onclick="runExec()">▶ Run code</button>
  </div>
  <div id="exec-result" class="result-box"></div>
  <div class="explain" id="exec-explain" style="display:none"></div>
</div>

<!-- ══ COMMAND INJECTION ══ -->
<div id="p-cmd" class="page">
  <div class="card">
    <div class="ct">OS command injection — file viewer</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:.875rem">A file viewer that builds a shell command by concatenating user input. The vulnerable version allows chaining extra commands using <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">;</code> <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">&&</code> <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">|</code></p>
    <div class="mode-row">
      <button class="mode-btn vuln on" id="cmd-vuln-btn" onclick="setMode('cmd','vuln')">❌ Vulnerable</button>
      <button class="mode-btn safe" id="cmd-safe-btn" onclick="setMode('cmd','safe')">✅ Secure</button>
    </div>
    <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:5px">Filename</label>
    <input type="text" id="cmd-input" value="report.txt" placeholder="Enter filename...">
    <div class="ct" style="margin-top:.875rem;margin-bottom:6px">Quick payloads</div>
    <div class="chip-row" id="cmd-chips"></div>
    <button class="btn bl btn-full" style="margin-top:.5rem" onclick="runCmd()">▶ View file</button>
  </div>
  <div id="cmd-result" class="result-box"></div>
  <div class="explain" id="cmd-explain" style="display:none"></div>
  <div class="card" style="margin-top:.75rem">
    <div class="ct">Generated command</div>
    <div class="query-box" id="cmd-query">—</div>
    <div class="compare" style="margin-top:.75rem">
      <div class="vuln-side">
        <div class="side-title">❌ Vulnerable</div>
        <div class="codeblock"><span style="color:#F85149">cmd = "cat /uploads/" + filename
os.system(cmd)
# filename = "x; rm -rf /"
# → catastrophic!</span></div>
      </div>
      <div class="safe-side">
        <div class="side-title">✅ Secure</div>
        <div class="codeblock"><span style="color:#3FB950">import re
if re.fullmatch(r'[\w\-\.]+', fname):
    subprocess.run(["cat", path],
        shell=False)  # no shell=True!</span></div>
      </div>
    </div>
  </div>
</div>

<!-- ══ FORMAT STRING ══ -->
<div id="p-format" class="page">
  <div class="card">
    <div class="ct">Format string injection</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:.875rem">When user input controls a Python format string, they can reference any variable name — including internal secrets passed to <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">.format(**config)</code>.</p>
    <div class="mode-row">
      <button class="mode-btn vuln on" id="format-vuln-btn" onclick="setMode('format','vuln')">❌ Vulnerable</button>
      <button class="mode-btn safe" id="format-safe-btn" onclick="setMode('format','safe')">✅ Secure</button>
    </div>
    <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:5px">Template string</label>
    <input type="text" id="format-input" value="Welcome {name}!" placeholder="e.g. Hello {name}">
    <label style="font-size:11px;color:var(--muted);display:block;margin:8px 0 5px">Your name</label>
    <input type="text" id="format-name" value="Alice" placeholder="name">
    <div class="ct" style="margin-top:.875rem;margin-bottom:6px">Quick payloads</div>
    <div class="chip-row" id="format-chips"></div>
    <button class="btn bl btn-full" style="margin-top:.5rem" onclick="runFormat()">▶ Render</button>
  </div>
  <div id="format-result" class="result-box"></div>
  <div class="explain" id="format-explain" style="display:none"></div>
</div>

<!-- ══ PICKLE ══ -->
<div id="p-pickle" class="page">
  <div class="card">
    <div class="ct">Pickle deserialization injection</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:.875rem">Python's <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">pickle.loads()</code> can execute arbitrary code via <code style="background:var(--bg3);padding:1px 5px;border-radius:3px">__reduce__</code>. Never deserialize untrusted pickle data.</p>
    <div class="mode-row">
      <button class="mode-btn vuln on" id="pickle-vuln-btn" onclick="setMode('pickle','vuln')">❌ Vulnerable</button>
      <button class="mode-btn safe" id="pickle-safe-btn" onclick="setMode('pickle','safe')">✅ Secure (JSON)</button>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:.875rem">
      <button class="btn bgray" style="flex:1" onclick="genPickle('safe')">📦 Safe pickle</button>
      <button class="btn br" style="flex:1" onclick="genPickle('malicious')">☠ Malicious pickle</button>
      <button class="btn bgr" style="flex:1;color:#000" onclick="genPickle('json')">✅ JSON payload</button>
    </div>
    <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:5px">Base64 payload</label>
    <textarea id="pickle-input" rows="3" placeholder="Base64 encoded payload..."></textarea>
    <button class="btn bl btn-full" style="margin-top:.75rem" onclick="runPickle()">▶ Deserialize</button>
  </div>
  <div id="pickle-result" class="result-box"></div>
  <div class="explain" id="pickle-explain" style="display:none"></div>
  <div class="card" style="margin-top:.75rem">
    <div class="compare">
      <div class="vuln-side">
        <div class="side-title">❌ Vulnerable</div>
        <div class="codeblock"><span style="color:#F85149">import pickle
obj = pickle.loads(user_data)
# __reduce__ runs on load
# → RCE!</span></div>
      </div>
      <div class="safe-side">
        <div class="side-title">✅ Secure</div>
        <div class="codeblock"><span style="color:#3FB950">import json
obj = json.loads(user_data)
# JSON cannot execute code
# → safe!</span></div>
      </div>
    </div>
  </div>
</div>

<!-- ══ SSTI ══ -->
<div id="p-ssti" class="page">
  <div class="card">
    <div class="ct">Server-side template injection (SSTI)</div>
    <p style="font-size:12px;color:var(--muted);margin-bottom:.875rem">When user input is embedded directly into a template string, Python's attribute chain can be exploited to access class internals and globals.</p>
    <div class="mode-row">
      <button class="mode-btn vuln on" id="ssti-vuln-btn" onclick="setMode('ssti','vuln')">❌ Vulnerable</button>
      <button class="mode-btn safe" id="ssti-safe-btn" onclick="setMode('ssti','safe')">✅ Secure</button>
    </div>
    <label style="font-size:11px;color:var(--muted);display:block;margin-bottom:5px">Your name</label>
    <input type="text" id="ssti-name" value="Alice">
    <label style="font-size:11px;color:var(--muted);display:block;margin:8px 0 5px">Template</label>
    <input type="text" id="ssti-template" value="Hello {name}!" placeholder="{name}">
    <div class="ct" style="margin-top:.875rem;margin-bottom:6px">Quick payloads</div>
    <div class="chip-row" id="ssti-chips"></div>
    <button class="btn bl btn-full" style="margin-top:.5rem" onclick="runSSTI()">▶ Render template</button>
  </div>
  <div id="ssti-result" class="result-box"></div>
  <div class="explain" id="ssti-explain" style="display:none"></div>
</div>

<!-- ══ MORE ══ -->
<div id="p-more" class="page">
  <div class="card">
    <div class="ct">All injection types covered</div>
    <table style="width:100%;font-size:12px;border-collapse:collapse">
      <tr style="border-bottom:1px solid var(--bdr)"><th style="padding:8px;text-align:left;background:var(--bg3)">Type</th><th style="padding:8px;text-align:left;background:var(--bg3)">Root cause</th><th style="padding:8px;text-align:left;background:var(--bg3)">Fix</th></tr>
      <tr style="border-bottom:1px solid var(--bg3)"><td style="padding:8px">eval()</td><td style="padding:8px;color:var(--muted)">Unsanitised input to eval</td><td style="padding:8px;color:var(--green)">Whitelist regex</td></tr>
      <tr style="border-bottom:1px solid var(--bg3)"><td style="padding:8px">exec()</td><td style="padding:8px;color:var(--muted)">Arbitrary code execution</td><td style="padding:8px;color:var(--green)">AST analysis + sandbox</td></tr>
      <tr style="border-bottom:1px solid var(--bg3)"><td style="padding:8px">Command injection</td><td style="padding:8px;color:var(--muted)">shell=True + user input</td><td style="padding:8px;color:var(--green)">Whitelist + no shell=True</td></tr>
      <tr style="border-bottom:1px solid var(--bg3)"><td style="padding:8px">Format string</td><td style="padding:8px;color:var(--muted)">.format(**secrets)</td><td style="padding:8px;color:var(--green)">Restrict allowed variables</td></tr>
      <tr style="border-bottom:1px solid var(--bg3)"><td style="padding:8px">Pickle RCE</td><td style="padding:8px;color:var(--muted)">__reduce__ on load</td><td style="padding:8px;color:var(--green)">Use JSON instead</td></tr>
      <tr><td style="padding:8px">SSTI</td><td style="padding:8px;color:var(--muted)">User controls template</td><td style="padding:8px;color:var(--green)">Whitelist placeholders</td></tr>
    </table>
  </div>
  <div class="disc">
    <h3>⚠️ Legal disclaimer</h3>
    <p>All demos are local sandbox only. Never apply these techniques to real applications without explicit written permission. Karanam Shrivasta assumes zero liability for misuse.</p>
  </div>
  <div class="wm">
    <div class="n">Made by Karanam Shrivasta</div>
    <div class="r">Network Security Educator · Ethical Hacking Researcher</div>
    <div><a href="https://www.linkedin.com/in/karanam-shrivasta/" target="_blank">LinkedIn</a><a href="https://github.com/mrshrivasta" target="_blank">GitHub</a></div>
  </div>
</div>

</div><!-- /main -->

<div class="bbar">
  <button class="btab on" data-p="p-overview" onclick="switchTab(this)"><span class="ico">🏠</span><span class="lbl">Overview</span></button>
  <button class="btab" data-p="p-eval" onclick="switchTab(this)"><span class="ico">🧮</span><span class="lbl">eval()</span></button>
  <button class="btab" data-p="p-exec" onclick="switchTab(this)"><span class="ico">⚡</span><span class="lbl">exec()</span></button>
  <button class="btab" data-p="p-cmd" onclick="switchTab(this)"><span class="ico">💻</span><span class="lbl">Command</span></button>
  <button class="btab" data-p="p-format" onclick="switchTab(this)"><span class="ico">📝</span><span class="lbl">Format</span></button>
  <button class="btab" data-p="p-pickle" onclick="switchTab(this)"><span class="ico">🥒</span><span class="lbl">Pickle</span></button>
  <button class="btab" data-p="p-ssti" onclick="switchTab(this)"><span class="ico">🌐</span><span class="lbl">SSTI</span></button>
  <button class="btab" data-p="p-more" onclick="switchTab(this)"><span class="ico">⋯</span><span class="lbl">More</span></button>
</div>

<script>
// ── tabs ──────────────────────────────────────────────
function switchTab(btn){
  document.querySelectorAll('.btab').forEach(b=>b.classList.remove('on'));
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById(btn.dataset.p).classList.add('on');
  document.getElementById('scroll').scrollTop=0;
}

// ── theme ─────────────────────────────────────────────
let DARK=true;
function toggleTheme(){
  DARK=!DARK;
  document.documentElement.setAttribute('data-theme',DARK?'dark':'light');
  document.getElementById('theme-btn').textContent=DARK?'🌙':'☀️';
}

// ── mode state ────────────────────────────────────────
const modes={eval:'vuln',exec:'vuln',cmd:'vuln',format:'vuln',pickle:'vuln',ssti:'vuln'};
function setMode(page,mode){
  modes[page]=mode;
  document.getElementById(page+'-vuln-btn').classList.toggle('on',mode==='vuln');
  document.getElementById(page+'-safe-btn').classList.toggle('on',mode==='safe');
}

// ── payloads ──────────────────────────────────────────
let PAYLOADS={};
async function loadPayloads(){
  PAYLOADS=await (await fetch('/api/payloads')).json();
  renderOverview();
  renderChips('eval','eval-chips','eval-input',null);
  renderChips('exec','exec-chips',null,'exec-input');
  renderChips('cmd','cmd-chips','cmd-input',null);
  renderChips('format','format-chips','format-input',null);
  renderChips('ssti','ssti-chips','ssti-template',null);
}

function renderOverview(){
  const INFO={
    eval:{icon:'🧮',title:'eval() Injection',desc:'User input passed to Python eval() — can execute arbitrary expressions and import modules.'},
    exec:{icon:'⚡',title:'exec() Injection',desc:'User controls code run via exec() — can import os, open files, or spawn processes.'},
    cmd:{icon:'💻',title:'Command Injection',desc:'Filename concatenated into shell command — semicolons and pipes chain extra commands.'},
    format:{icon:'📝',title:'Format String',desc:'User controls .format() template — can access secret variables by name.'},
    pickle:{icon:'🥒',title:'Pickle RCE',desc:'Malicious pickle uses __reduce__ to execute code on deserialization.'},
    ssti:{icon:'🌐',title:'SSTI',desc:'User-supplied template accesses Python class internals via attribute chains.'},
  };
  const tabs=['p-eval','p-exec','p-cmd','p-format','p-pickle','p-ssti'];
  document.getElementById('ov-cards').innerHTML=Object.entries(INFO).map(([k,v],i)=>`
    <div class="ov-card" onclick="document.querySelectorAll('.btab')[${i+1}].click()">
      <div class="ov-icon">${v.icon}</div>
      <div>
        <div style="font-size:13px;font-weight:700;margin-bottom:3px">${v.title}</div>
        <div style="font-size:12px;color:var(--muted);line-height:1.5">${v.desc}</div>
      </div>
    </div>`).join('');
}

function renderChips(key, containerId, singleInput, multiInput){
  const list=PAYLOADS[key]||[];
  const el=document.getElementById(containerId);
  if(!el) return;
  el.innerHTML=list.map((p,i)=>{
    const cls=p.expect==='safe'?'safe-c':p.expect==='blocked'?'':'danger';
    const short=(p.payload||'').replace(/\n/g,' ').substring(0,30);
    return `<div class="chip ${cls}" onclick="applyPayload('${key}','${singleInput||multiInput}',${i},'${singleInput?'single':'multi'}')" title="${p.desc}">${short}${p.payload.length>30?'…':''}</div>`;
  }).join('');
}

function applyPayload(key,inputId,idx,type){
  const p=PAYLOADS[key][idx];
  const el=document.getElementById(inputId);
  if(el) el.value=p.payload;
}

// ── result renderer ───────────────────────────────────
function showResult(id, data, explainId, explainText){
  const el=document.getElementById(id);
  el.style.display='block';
  let cls='normal', icon='', text='';

  if(data.error){
    const isBlocked=data.error.toLowerCase().includes('block')||data.error.toLowerCase().includes('reject');
    cls=isBlocked?'blocked':'danger';
    icon=isBlocked?'🛡️ BLOCKED':'❌ ERROR';
    text=`${icon}\n${data.error}`;
  } else if(data.injected){
    cls='danger'; icon='⚠️ INJECTION DETECTED';
    text=`${icon}\n\nCommand: ${data.cmd}\n\n${data.output}`;
  } else if(data.leaked){
    cls='danger'; icon='🔓 SECRET LEAKED';
    text=`${icon}\nRendered: ${data.rendered||data.output}`;
  } else if(data.dangerous){
    cls='danger'; icon='⚠️ CODE EXECUTED';
    text=`${icon}\nOutput: ${data.output}`;
  } else {
    cls='safe-res'; icon='✅';
    const out=data.result||data.output||data.rendered||data.object_type||'OK';
    text=`${icon} ${out}`;
  }
  el.className='result-box '+cls;
  el.textContent=text;

  const expEl=document.getElementById(explainId);
  if(explainText){expEl.textContent=explainText;expEl.style.display='block';}
  else expEl.style.display='none';
}

// ── eval ──────────────────────────────────────────────
async function runEval(){
  const expr=document.getElementById('eval-input').value;
  const r=await fetch('/api/eval',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:modes.eval,expr})});
  const d=await r.json();
  const explain=modes.eval==='vuln'&&d.error&&d.error.includes("'os'")?
    "The eval() function executed __import__('os') — this is real code execution. An attacker could read files, list directories, or even open network connections.":
    modes.eval==='safe'&&d.error?
    "The whitelist regex rejected the input before eval() was called. Only [0-9 + - * / . ( )] are allowed — no function calls, imports, or string literals.":"";
  showResult('eval-result',d,'eval-explain',explain);
}

// ── exec ──────────────────────────────────────────────
async function runExec(){
  const code=document.getElementById('exec-input').value;
  const r=await fetch('/api/exec',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:modes.exec,code})});
  const d=await r.json();
  const explain=modes.exec==='safe'&&d.error&&d.error.includes('Blocked')?
    "AST analysis caught the forbidden node before execution. The code was parsed into an abstract syntax tree and each node type was checked — Import and file-related Names are banned.":"";
  showResult('exec-result',d,'exec-explain',explain);
}

// ── cmd ───────────────────────────────────────────────
async function runCmd(){
  const filename=document.getElementById('cmd-input').value;
  const r=await fetch('/api/cmd',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:modes.cmd,filename})});
  const d=await r.json();
  document.getElementById('cmd-query').textContent='$ '+d.cmd;
  const explain=d.injected?
    "Shell metacharacters (;, &&, |, `, $()) were detected in the filename. In a real vulnerable app, these would chain additional OS commands — potentially reading /etc/passwd, deleting files, or opening a reverse shell.":
    modes.cmd==='safe'&&d.error?
    "The whitelist regex rejects any character that isn't alphanumeric, hyphen, dot, or underscore. The command is also called without shell=True — so even if the regex were bypassed, the shell wouldn't interpret metacharacters.":"";
  showResult('cmd-result',d,'cmd-explain',explain);
}

// ── format ────────────────────────────────────────────
async function runFormat(){
  const template=document.getElementById('format-input').value;
  const name=document.getElementById('format-name').value;
  const r=await fetch('/api/format',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:modes.format,template,name})});
  const d=await r.json();
  const explain=d.leaked?
    "Python's .format(**config) passes all internal config variables into scope. By guessing a variable name like {db_password}, an attacker reads secrets that were never meant to be visible.":
    d.error?
    "Safe mode only passes {name} and {app} into the template context — even if you write {db_password}, there's no such variable available to the format call.":"";
  showResult('format-result',d,'format-explain',explain);
}

// ── pickle ────────────────────────────────────────────
async function genPickle(type){
  const r=await fetch('/api/pickle',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({action:type==='safe'?'make_safe':type==='malicious'?'make_malicious':'make_json'})});
  const d=await r.json();
  document.getElementById('pickle-input').value=d.payload;
  const expEl=document.getElementById('pickle-explain');
  expEl.style.display='block';
  expEl.textContent=type==='malicious'?
    "This payload uses __reduce__ to inject a function call (print here; in a real attack it would be os.system('malicious command')). When pickle.loads() encounters it, it executes the payload immediately — before you even inspect the object.":
    type==='json'?
    "JSON is safe because it can only represent data structures — strings, numbers, lists, dicts. There's no mechanism to encode function calls or execute code during parsing.":
    "A normal serialized Python object with name and role attributes. No exploit code.";
}

async function runPickle(){
  const payload=document.getElementById('pickle-input').value.trim();
  if(!payload){alert('Generate a payload first.');return;}
  const r=await fetch('/api/pickle',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:modes.pickle,payload})});
  const d=await r.json();
  showResult('pickle-result',d,'pickle-explain','');
}

// ── ssti ──────────────────────────────────────────────
async function runSSTI(){
  const name=document.getElementById('ssti-name').value;
  const template=document.getElementById('ssti-template').value;
  const r=await fetch('/api/template',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:modes.ssti,name,template})});
  const d=await r.json();
  const explain=d.error&&!d.rendered?
    "SSTI exploits Python's attribute introspection. {name.__class__.__mro__} walks up the class hierarchy. From there, attackers find file-reader or subprocess classes to execute OS commands. Jinja2 on Flask is particularly vulnerable to this attack pattern.":
    modes.ssti==='safe'&&d.error?
    "Safe mode validates each placeholder against a whitelist. Only {name} and {greeting} are allowed — any other format expression is rejected before rendering.":"";
  showResult('ssti-result',d,'ssti-explain',explain);
}

// ── init ──────────────────────────────────────────────
loadPayloads();
</script>
</body>
</html>"""

if __name__ == "__main__":
    app.run(debug=False, port=5000, threaded=True)