"""brief_lint.py (ai-collab 0.2.0): 只讀掃一份交辦單的寫法，不叫 AI。結果只是提醒，不算 Pro 放行，也不保證理解一致。
python -B brief_lint.py <交辦單>
掃的五件事：
 1. 出現某家 AI 的工具名稱（references/actions.json 的 tool_names），寫成指令（「用 X」「X 工具」「以 X 讀／寫」）
 2. 提到檔案路徑，同一行沒有附 SHA256（64 個十六進位字，或至少 8 個十六進位字的開頭）
 3. 引用使用者原話（「使用者…說／回／原話」或「…」裡的話標成使用者的），同一行沒有行號或 uuid
 4. 出現詞典 references/terms.json 標為禁用的寫法
 5. 缺少「必讀」或「收到確認」那一段（## 標題）
輸出 JSON：ok、warnings（每項有 rule、line、text）。有提醒時結束碼 1。"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, '..', 'references')
PATH = re.compile(r'(?:[A-Za-z]:\\[^\s，。；、）)」]+|(?:\.{0,2}/)?[\w.\-]+(?:/[\w.\-]+)+\.\w+)')
HASH = re.compile(r'(?<![0-9a-fA-F])[0-9a-fA-F]{8,64}(?![0-9a-fA-F])')
QUOTE_USER = re.compile(r'使用者[^。\n]{0,8}?(說|回|原話|寫|打)')
WHERE = re.compile(r'(第\s*\d+\s*行|行號\s*\d+|[0-9a-f]{8}-[0-9a-f]{4}-|uuid)', re.I)


def load(name):
    with open(os.path.join(REF, name), encoding='utf-8-sig') as f:
        return json.load(f)


def strip_code(lines):
    out, fence = [], False
    for i, l in enumerate(lines, 1):
        if l.lstrip().startswith('```'):
            fence = not fence
            continue
        out.append((i, '' if fence else l))
    return out


def main(argv):
    if len(argv) != 2:
        print(json.dumps({'ok': False, 'warnings': [{'rule': 0, 'line': 0, 'text': '用法：brief_lint.py <交辦單>'}]}, ensure_ascii=False))
        return 2
    try:
        with open(argv[1], encoding='utf-8-sig') as f:
            raw = f.read()
        actions, terms = load('actions.json'), load('terms.json')
    except (OSError, ValueError) as e:
        print(json.dumps({'ok': False, 'warnings': [{'rule': 0, 'line': 0, 'text': f'讀不到檔：{e}'}]}, ensure_ascii=False))
        return 2
    lines = raw.splitlines(); body = strip_code(lines); warn = []
    def add(rule, i, text): warn.append({'rule': rule, 'line': i, 'text': text})
    tools = actions.get('tool_names', [])
    for i, l in body:
        for t in tools:
            if re.search(r'(用\s*' + re.escape(t) + r'(?![A-Za-z])|(?<![A-Za-z])' + re.escape(t) + r'\s*工具|以\s*' + re.escape(t) + r'(?![A-Za-z]))', l):
                add(1, i, f'寫了工具名稱「{t}」，改寫成 actions.json 的通用動作')
        if PATH.search(l) and not HASH.search(l):
            add(2, i, '提到檔案路徑，這一行沒有附 SHA256')
        if QUOTE_USER.search(l) and not WHERE.search(l):
            add(3, i, '引用使用者的話，這一行沒有行號或 uuid')
        for key, term in terms.get('terms', {}).items():
            for bad in term.get('banned', []):
                pat = (r'(?<![A-Za-z0-9])' + re.escape(bad) + r'(?![A-Za-z0-9])') if re.fullmatch(r'[A-Za-z0-9 ]+', bad) else re.escape(bad)
                if re.search(pat, l, flags=re.I):
                    add(4, i, f'用了「{bad}」，詞典寫「{key}」')
    heads = [l.strip() for l in lines if l.startswith('## ')]
    for need in ('必讀', '收到確認'):
        if not any(need in h for h in heads):
            add(5, 0, f'缺少「## {need}」那一段')
    print(json.dumps({'ok': not warn, 'file': argv[1], 'version': '0.2.0', 'warnings': warn,
                      'note': '只是寫法提醒，不算 Pro 放行，也不保證理解一致'}, ensure_ascii=False))
    return 0 if not warn else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
