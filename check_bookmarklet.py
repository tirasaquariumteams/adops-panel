# -*- coding: utf-8 -*-
"""Проверка кода закладки ТАК, как его хранит браузер: переводы строк удаляются при перетаскивании,
поэтому строчный комментарий // «съедает» весь код после себя. Прогоняем node --check по склеенной строке.
    python3 check_bookmarklet.py [index.html]"""
import re, subprocess, sys, tempfile, os
p = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
t = open(p, encoding='utf-8').read()
ok = True
for sid in ('src', 'src2'):
    m = re.search(r'<script id="%s" type="text/plain">(.*?)</script>' % sid, t, re.S)
    if not m: print('%s: блока нет' % sid); continue
    code = m.group(1).strip()
    if not code.startswith('javascript:'): print('%s: не начинается с javascript:' % sid); ok = False; continue
    body = code[len('javascript:'):]
    if re.search(r'(^|[;{}()\s])//(?!/)', body, re.M) and sid == 'src':
        print('%s: найден строчный комментарий // — после склейки строк он сломает код' % sid); ok = False
    for label, variant in (('с переводами строк', body), ('одной строкой (как в закладке)', body.replace('\r', '').replace('\n', ''))):
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(variant); path = f.name
        r = subprocess.run(['node', '--check', path], capture_output=True, text=True); os.unlink(path)
        if r.returncode: print('%s %s: ОШИБКА\n%s' % (sid, label, r.stderr[:400])); ok = False
        else: print('%s %s: ok (%d символов)' % (sid, label, len(variant)))
sys.exit(0 if ok else 1)
