#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_files.py — يصلح كل ملفات HTML في الموقع تلقائياً
يُشغَّل من GitHub Actions عند كل push
"""

import os
import re

# ===== القاعدة: normalize الصحيحة =====
CORRECT_NORMALIZE = """function normalize(str){if(!str)return'';return str.replace(/ـ/g,'').replace(/وٰ/g,'و').replace(/اٰ/g,'ا').replace(/يٰ/g,'ي').replace(/ىٰ/g,'ا').replace(/(.)ٰ/g,'$1ا').replace(/هۥ/g,'ه').replace(/هۦ/g,'ه').replace(/[ۥۦ]/g,'').replace(/[ئؤ]/g,'ء').replace(/ء/g,'').replace(/[آأإٱا]/g,'ا').replace(/[ىی]/g,'ي').replace(/ة/g,'ه').replace(/[\\u064B-\\u065F\\u0610-\\u061A\\u06D6-\\u06DC\\u06DF-\\u06E4\\u06E7\\u06E8\\u06EA-\\u06ED]/g,'').replace(/(.)\x5c1+/g,'$1').replace(/رحمان/g,'رحمن').replace(/هاؤلاء/g,'هولا').replace(/هؤلاء/g,'هولا').replace(/ياايها/g,'يايها').replace(/يا ايها/g,'يايها').replace(/هاذا/g,'هذا').replace(/ذالك/g,'ذلك').replace(/\\s+/g,' ').trim();}"""

CORRECT_NM = """const nm=s=>{if(!s)return'';return s.replace(/ـ/g,'').replace(/وٰ/g,'و').replace(/اٰ/g,'ا').replace(/يٰ/g,'ي').replace(/ىٰ/g,'ا').replace(/(.)ٰ/g,'$1ا').replace(/هۥ/g,'ه').replace(/هۦ/g,'ه').replace(/[ۥۦ]/g,'').replace(/[ئؤ]/g,'ء').replace(/ء/g,'').replace(/[آأإٱا]/g,'ا').replace(/[ىی]/g,'ي').replace(/ة/g,'ه').replace(/[\\u064B-\\u065F\\u0610-\\u061A\\u06D6-\\u06DC\\u06DF-\\u06E4\\u06E7\\u06E8\\u06EA-\\u06ED]/g,'').replace(/(.)\x5c1+/g,'$1').replace(/رحمان/g,'رحمن').replace(/هاؤلاء/g,'هولا').replace(/هؤلاء/g,'هولا').replace(/ياايها/g,'يايها').replace(/يا ايها/g,'يايها').replace(/هاذا/g,'هذا').replace(/ذالك/g,'ذلك').replace(/\\s+/g,' ').trim();};"""

# زر اختر مستوى آخر
LEVEL_RETURN_BTN = '<button class="level-return-btn" onclick="returnToLevels()">🔄 اختر مستوى آخر</button>'

# CSS زر اختر مستوى
LEVEL_RETURN_CSS = '.level-return-btn{display:block;width:100%;margin-top:14px;padding:11px;background:var(--surface2);color:var(--text-soft);border:1.5px solid var(--border);border-radius:12px;font-size:15px;font-family:inherit;cursor:pointer;transition:all .2s;text-align:center;}\n.level-return-btn:hover{background:var(--surface-hover);border-color:var(--accent);color:var(--accent);}'

# دالة returnToLevels
RETURN_TO_LEVELS_FN = """function returnToLevels(){document.getElementById('quiz-area').style.display='none';document.getElementById('level-card').style.display='block';currentLevel=null;document.querySelectorAll('.level-btn').forEach(b=>b.classList.remove('active'));document.getElementById('start-btn').classList.remove('ready');document.getElementById('total-q').textContent='-';document.getElementById('wrong-badge').innerHTML='٠ ✗<br>خطأ';document.getElementById('correct-badge').innerHTML='٠ ✓<br>صحيح';document.getElementById('qnum-badge').innerHTML='السؤال ١ /<br>-';document.getElementById('progress-fill').style.width='0%';}"""


def fix_normalize(content):
    """يصلح دالة normalize() الرئيسية"""
    # نمط يطابق أي نسخة من normalize
    pattern = r'function normalize\(str\)\{[^}]+(?:\}[^}]*)*?\}'
    if re.search(pattern, content):
        content = re.sub(pattern, CORRECT_NORMALIZE, content, count=1)
    return content


def fix_nm_in_worddiff(content):
    """يصلح دالة nm داخل wordDiff"""
    pattern = r'const nm=s=>\{[^}]+(?:\}[^}]*)*?\};'
    if re.search(pattern, content):
        content = re.sub(pattern, CORRECT_NM, content, count=1)
    return content


def fix_level_return_btn(content):
    """يضيف زر اختر مستوى آخر إن لم يكن موجوداً"""
    if 'returnToLevels' in content:
        return content  # موجود بالفعل

    # يضيفه بعد div الـ feedback مباشرة
    feedback_pattern = r'(<div class="feedback" id="feedback"></div>)'
    replacement = r'\1\n  ' + LEVEL_RETURN_BTN
    if re.search(feedback_pattern, content):
        content = re.sub(feedback_pattern, replacement, content, count=1)

    return content


def fix_level_return_css(content):
    """يضيف CSS زر اختر مستوى إن لم يكن موجوداً"""
    if 'level-return-btn' in content:
        return content
    # يضيفه قبل </style>
    content = content.replace('</style>', LEVEL_RETURN_CSS + '\n</style>', 1)
    return content


def fix_return_to_levels_fn(content):
    """يضيف دالة returnToLevels إن لم تكن موجودة"""
    if 'function returnToLevels' in content:
        return content
    # يضيفها قبل دالة retryQuiz
    if 'function retryQuiz' in content:
        content = content.replace(
            'function retryQuiz',
            RETURN_TO_LEVELS_FN + '\n' + 'function retryQuiz',
            1
        )
    return content


def should_fix(filename):
    """يحدد الملفات اللي المفروض تتصلح"""
    skip = ['index.html', 'recitation.html', 'scripts/', '.github/']
    for s in skip:
        if s in filename:
            return False
    return filename.endswith('.html')


def fix_file(filepath):
    """يطبق كل الإصلاحات على ملف واحد"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        print(f'  ✗ خطأ في القراءة: {e}')
        return False

    content = original

    # تطبيق الإصلاحات
    content = fix_normalize(content)
    content = fix_nm_in_worddiff(content)
    content = fix_level_return_css(content)
    content = fix_level_return_btn(content)
    content = fix_return_to_levels_fn(content)

    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'  ✓ تم إصلاح: {os.path.basename(filepath)}')
            return True
        except Exception as e:
            print(f'  ✗ خطأ في الكتابة: {e}')
            return False
    else:
        print(f'  — لا تغيير: {os.path.basename(filepath)}')
        return False


def main():
    # مسار الملفات — الجذر في GitHub Actions
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f'📁 المجلد: {root}')

    fixed = 0
    skipped = 0

    for filename in sorted(os.listdir(root)):
        filepath = os.path.join(root, filename)
        if not os.path.isfile(filepath):
            continue
        if not should_fix(filepath):
            continue

        result = fix_file(filepath)
        if result:
            fixed += 1
        else:
            skipped += 1

    print(f'\n✅ تم إصلاح {fixed} ملف — {skipped} بدون تغيير')


if __name__ == '__main__':
    main()
