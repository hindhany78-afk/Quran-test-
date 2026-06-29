#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re

# normalize الصحيحة - موضعين في كل ملف
NORMALIZE_FN = (
    "function normalize(str){if(!str)return'';"
    "return str.replace(/\u0640/g,'')"
    ".replace(/\u0648\u0670/g,'\u0648')"
    ".replace(/\u0627\u0670/g,'\u0627')"
    ".replace(/\u064a\u0670/g,'\u064a')"
    ".replace(/\u0649\u0670/g,'\u0627')"
    ".replace(/(.)\\u0670/g,'$1\u0627')"
    ".replace(/\u0647\u06e5/g,'\u0647')"
    ".replace(/\u0647\u06e6/g,'\u0647')"
    ".replace(/[\u06e5\u06e6]/g,'')"
    ".replace(/[\u0626\u0624]/g,'\u0621')"
    ".replace(/\u0621/g,'')"
    ".replace(/[\u0622\u0623\u0625\u0671\u0627]/g,'\u0627')"
    ".replace(/[\u0649\u06cc]/g,'\u064a')"
    ".replace(/\u0629/g,'\u0647')"
    ".replace(/[\\u064B-\\u065F\\u0610-\\u061A\\u06D6-\\u06DC\\u06DF-\\u06E4\\u06E7\\u06E8\\u06EA-\\u06ED]/g,'')"
    ".replace(/(.)\x5c1+/g,'$1')"
    ".replace(/\u0631\u062d\u0645\u0627\u0646/g,'\u0631\u062d\u0645\u0646')"
    ".replace(/\u0647\u0627\u0624\u0644\u0627\u0621/g,'\u0647\u0648\u0644\u0627')"
    ".replace(/\u0647\u0624\u0644\u0627\u0621/g,'\u0647\u0648\u0644\u0627')"
    ".replace(/\u064a\u0627\u0627\u064a\u0647\u0627/g,'\u064a\u0627\u064a\u0647\u0627')"
    ".replace(/\u064a\u0627 \u0627\u064a\u0647\u0627/g,'\u064a\u0627\u064a\u0647\u0627')"
    ".replace(/\u0647\u0627\u0630\u0627/g,'\u0647\u0630\u0627')"
    ".replace(/\u0630\u0627\u0644\u0643/g,'\u0630\u0644\u0643')"
    ".replace(/\\s+/g,' ').trim();}"
)

NM_FN = (
    "const nm=s=>{if(!s)return'';"
    "return s.replace(/\u0640/g,'')"
    ".replace(/\u0648\u0670/g,'\u0648')"
    ".replace(/\u0627\u0670/g,'\u0627')"
    ".replace(/\u064a\u0670/g,'\u064a')"
    ".replace(/\u0649\u0670/g,'\u0627')"
    ".replace(/(.)\\u0670/g,'$1\u0627')"
    ".replace(/\u0647\u06e5/g,'\u0647')"
    ".replace(/\u0647\u06e6/g,'\u0647')"
    ".replace(/[\u06e5\u06e6]/g,'')"
    ".replace(/[\u0626\u0624]/g,'\u0621')"
    ".replace(/\u0621/g,'')"
    ".replace(/[\u0622\u0623\u0625\u0671\u0627]/g,'\u0627')"
    ".replace(/[\u0649\u06cc]/g,'\u064a')"
    ".replace(/\u0629/g,'\u0647')"
    ".replace(/[\\u064B-\\u065F\\u0610-\\u061A\\u06D6-\\u06DC\\u06DF-\\u06E4\\u06E7\\u06E8\\u06EA-\\u06ED]/g,'')"
    ".replace(/(.)\x5c1+/g,'$1')"
    ".replace(/\u0631\u062d\u0645\u0627\u0646/g,'\u0631\u062d\u0645\u0646')"
    ".replace(/\u0647\u0627\u0624\u0644\u0627\u0621/g,'\u0647\u0648\u0644\u0627')"
    ".replace(/\u0647\u0624\u0644\u0627\u0621/g,'\u0647\u0648\u0644\u0627')"
    ".replace(/\u064a\u0627\u0627\u064a\u0647\u0627/g,'\u064a\u0627\u064a\u0647\u0627')"
    ".replace(/\u064a\u0627 \u0627\u064a\u0647\u0627/g,'\u064a\u0627\u064a\u0647\u0627')"
    ".replace(/\u0647\u0627\u0630\u0627/g,'\u0647\u0630\u0627')"
    ".replace(/\u0630\u0627\u0644\u0643/g,'\u0630\u0644\u0643')"
    ".replace(/\\s+/g,' ').trim();};"
)

LEVEL_RETURN_BTN = '\n  <button class="level-return-btn" onclick="returnToLevels()">\U0001f504 \u0627\u062e\u062a\u0631 \u0645\u0633\u062a\u0648\u0649 \u0622\u062e\u0631</button>'

LEVEL_RETURN_CSS = (
    '.level-return-btn{display:block;width:100%;margin-top:14px;padding:11px;'
    'background:var(--surface2);color:var(--text-soft);border:1.5px solid var(--border);'
    'border-radius:12px;font-size:15px;font-family:inherit;cursor:pointer;transition:all .2s;text-align:center;}\n'
    '.level-return-btn:hover{background:var(--surface-hover);border-color:var(--accent);color:var(--accent);}'
)

RETURN_TO_LEVELS = (
    "function returnToLevels(){"
    "document.getElementById('quiz-area').style.display='none';"
    "document.getElementById('level-card').style.display='block';"
    "currentLevel=null;"
    "document.querySelectorAll('.level-btn').forEach(b=>b.classList.remove('active'));"
    "document.getElementById('start-btn').classList.remove('ready');"
    "document.getElementById('total-q').textContent='-';"
    "document.getElementById('wrong-badge').innerHTML='\u06f0 \u2717<br>\u062e\u0637\u0623';"
    "document.getElementById('correct-badge').innerHTML='\u06f0 \u2713<br>\u0635\u062d\u064a\u062d';"
    "document.getElementById('qnum-badge').innerHTML='\u0627\u0644\u0633\u0624\u0627\u0644 \u06f1 /<br>-';"
    "document.getElementById('progress-fill').style.width='0%';}"
)


def fix_normalize(content):
    pattern = r'function normalize\(str\)\{if\(.*?\.trim\(\);\}'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, NORMALIZE_FN, content, count=1, flags=re.DOTALL)
    return content


def fix_nm(content):
    pattern = r'const nm=s=>\{if\(.*?\.trim\(\);\};'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, NM_FN, content, count=1, flags=re.DOTALL)
    return content


def fix_return_btn(content):
    if 'returnToLevels' in content:
        return content
    old = '<div class="feedback" id="feedback"></div>'
    new = old + LEVEL_RETURN_BTN
    content = content.replace(old, new, 1)
    return content


def fix_return_css(content):
    if 'level-return-btn' in content:
        return content
    content = content.replace('</style>', LEVEL_RETURN_CSS + '\n</style>', 1)
    return content


def fix_return_fn(content):
    if 'function returnToLevels' in content:
        return content
    content = content.replace(
        'function retryQuiz',
        RETURN_TO_LEVELS + '\n' + 'function retryQuiz',
        1
    )
    return content


def should_fix(filename):
    skip = ['index.html', 'recitation.html']
    if filename in skip:
        return False
    return filename.endswith('.html')


def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        print(f'  ERROR reading: {e}')
        return False

    content = original
    content = fix_normalize(content)
    content = fix_nm(content)
    content = fix_return_css(content)
    content = fix_return_btn(content)
    content = fix_return_fn(content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  FIXED: {os.path.basename(filepath)}')
        return True
    else:
        print(f'  OK: {os.path.basename(filepath)}')
        return False


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f'Root: {root}')
    fixed = 0
    for filename in sorted(os.listdir(root)):
        filepath = os.path.join(root, filename)
        if os.path.isfile(filepath) and should_fix(filename):
            if fix_file(filepath):
                fixed += 1
    print(f'Done: {fixed} files fixed')


if __name__ == '__main__':
    main()
