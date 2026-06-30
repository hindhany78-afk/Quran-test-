#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re

# ===== كود PWA يُضاف لكل ملف =====
PWA_HEAD = """<link rel="manifest" href="/Quran-test-/manifest.json">
<meta name="theme-color" content="#4a7c4a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="دربي">
<link rel="apple-touch-icon" href="/Quran-test-/icons/icon-192x192.png">"""

PWA_SW = """<script>
if('serviceWorker' in navigator){
  window.addEventListener('load',()=>{
    navigator.serviceWorker.register('/Quran-test-/service-worker.js')
      .then(r=>console.log('SW:',r.scope))
      .catch(e=>console.log('SW err:',e));
  });
}
</script>"""

def fix_file(path):
    with open(path, encoding='utf-8') as f:
        src = f.read()
    out = src

    # 0. قائمة التشكيل القديمة في قالب alburuj/altariq كانت ناقصة (مفيهاش حرف السكون
    #    ۡ المستخدم في خط جزء عمّ العثماني) فيفضل في الكلمة بعد التطبيع ويمنع التطابق
    #    — استبدلها بمدى يونيكود شامل (نفس قاعدة alnnas/recitation)، وقبلها قاعدة
    #    الهمزة على كشيدة (ـَٔ) لازم تتنفذ قبل حذف التشكيل عشان متضيعش
    out = out.replace(
        "replace(/[ًٌٍَُِّْٕٖٜٟٓٔٗ٘ٙٚٛٝٞۢ]/g,'')",
        r"replace(/ـ[\u064B-\u065F]*[\u0654\u0655]/g,'ا').replace(/[\u064B-\u065F\u0610-\u061A\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]/g,'')"
    )

    # 1. إصلاحات normalize/nm (تتطبق تلقائياً في الموضعين معاً):
    #    - ىٰ: لو جالها حرف بعدها في نفس الكلمة (زي أَدۡرَىٰكَ، أَلۡهَىٰكُمُ) = "ا"
    #      لو في آخر الكلمة (زي عَلَىٰ، أَغۡنَىٰ، سَيَصۡلَىٰ) = "ي" (زي باقي حالات ى)
    if "[ىی]ٰ(?=" not in out:
        out = re.sub(r"\[ىی\]ٰ/g,'[اي]'\)",
                      r"[ىی]ٰ(?=\\S)/g,'ا').replace(/[ىی]ٰ/g,'ي')",
                      out)

    #    - الهمزة المكتوبة فوق كشيدة (ـَٔ زي لَتُسۡـَٔلُنَّ) كانت بتتحذف بالكامل
    #      وتفقد الحرف؛ المفروض تتحول لـ"ا" (زي باقي حالات الهمزة على ألف)
    if r"[\u0654\u0655]/g,'ا')" not in out:
        out = out.replace(
            r".replace(/ـ/g,'')",
            r".replace(/ـ[\u064B-\u065F]*[\u0654\u0655]/g,'ا').replace(/ـ/g,'')"
        )

    #    - ۦ في وسط الكلمة (زي إِۦلَٰفِهِمۡ) = صوت ياء حقيقي = "ي"
    #      ۦ في آخر الكلمة (زي بِهِۦ، لِرَبِّهِۦ) = حرف صامت اختياري، تتقبل "به"/"بهي" الاتنين
    #      (ۥ تفضل تتحذف زي ما هي، دي مش نفس الحرف)
    if r"ۦ(?=\S)" not in out:
        out = out.replace(
            r".replace(/ه[ۥۦ]/g,'ه').replace(/[ۥۦ]/g,'')",
            r".replace(/ه[ۥۦ]/g,'ه').replace(/ۦ(?=\S)/g,'ي').replace(/ۦ/g,'').replace(/ۥ/g,'')"
        )
        out = out.replace(
            r".replace(/ه[ۥۦ]/g,'ه').replace(/ۦ/g,'ي').replace(/ۥ/g,'')",
            r".replace(/ه[ۥۦ]/g,'ه').replace(/ۦ(?=\S)/g,'ي').replace(/ۦ/g,'').replace(/ۥ/g,'')"
        )

    #    - كلمات خاصة: اله/إله، ارايت/أرءيت، يا أيها (تتكتب كلمتين وتتقبل ككلمة وحدة)
    if "replace(/يا ايها/g,'يايها')" not in out:
        out = out.replace(
            r".replace(/مولانا/g,'مولنا')",
            r".replace(/مولانا/g,'مولنا').replace(/يا ايها/g,'يايها').replace(/يا ايتها/g,'يايتها').replace(/الاه/g,'اله').replace(/ارايت/g,'اريت')"
        )

    # 1ب. نفس الإصلاحات لكن للصيغة الثانية من normalize/nm (زي alnnas.html وrecitation.html)
    if ".replace(/ىٰ(?=" not in out:
        out = re.sub(r"\.replace\(/ىٰ/g,'[اي]'\)",
                      r".replace(/ىٰ(?=\\S)/g,'ا').replace(/ىٰ/g,'ي')",
                      out)
    if r"ۦ(?=\S)" not in out:
        out = out.replace(
            r".replace(/هۦ/g,'ه').replace(/[ۥۦ]/g,'')",
            r".replace(/هۦ/g,'ه').replace(/ۦ(?=\S)/g,'ي').replace(/ۦ/g,'').replace(/ۥ/g,'')"
        )
        out = out.replace(
            r".replace(/هۦ/g,'ه').replace(/ۦ/g,'ي').replace(/ۥ/g,'')",
            r".replace(/هۦ/g,'ه').replace(/ۦ(?=\S)/g,'ي').replace(/ۦ/g,'').replace(/ۥ/g,'')"
        )
    if "replace(/الاه/g,'اله')" not in out:
        out = out.replace(
            r".replace(/ذالك/g,'ذلك')",
            r".replace(/ذالك/g,'ذلك').replace(/الاه/g,'اله').replace(/ارايت/g,'اريت')"
        )

    # 2. أضف زر returnToLevels لو مش موجود
    if 'returnToLevels' not in out:
        # CSS
        if 'level-return-btn' not in out:
            css = '.level-return-btn{display:block;width:100%;margin-top:14px;padding:11px;background:var(--surface2);color:var(--text-soft);border:1.5px solid var(--border);border-radius:12px;font-size:15px;font-family:inherit;cursor:pointer;transition:all .2s;text-align:center;}\n.level-return-btn:hover{background:var(--surface-hover);border-color:var(--accent);color:var(--accent);}'
            out = out.replace('</style>', css + '\n</style>', 1)
        # زر HTML
        btn = '\n  <button class="level-return-btn" onclick="returnToLevels()">&#x1F504; &#x627;&#x62E;&#x62A;&#x631; &#x645;&#x633;&#x62A;&#x648;&#x649; &#x622;&#x62E;&#x631;</button>'
        out = out.replace('<div class="feedback" id="feedback"></div>',
                         '<div class="feedback" id="feedback"></div>' + btn, 1)
        # دالة JS
        fn = """function returnToLevels(){document.getElementById('quiz-area').style.display='none';document.getElementById('level-card').style.display='block';currentLevel=null;document.querySelectorAll('.level-btn').forEach(b=>b.classList.remove('active'));document.getElementById('start-btn').classList.remove('ready');document.getElementById('total-q').textContent='-';document.getElementById('wrong-badge').innerHTML='&#x6F0; &#x2717;<br>&#x62E;&#x637;&#x623;';document.getElementById('correct-badge').innerHTML='&#x6F0; &#x2713;<br>&#x635;&#x62D;&#x64A;&#x62D;';document.getElementById('qnum-badge').innerHTML='&#x627;&#x644;&#x633;&#x624;&#x627;&#x644; &#x6F1; /<br>-';document.getElementById('progress-fill').style.width='0%';}"""
        out = out.replace('function retryQuiz', fn + '\nfunction retryQuiz', 1)

    # 3. أضف PWA head لو مش موجود
    if 'manifest.json' not in out:
        out = out.replace('</head>', PWA_HEAD + '\n</head>', 1)

    # 4. أضف Service Worker لو مش موجود
    if 'service-worker.js' not in out:
        out = out.replace('</body>', PWA_SW + '\n</body>', 1)

    if out != src:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
        return True
    return False

def fix_index_recitation(path):
    """index.html و recitation.html — PWA فقط"""
    with open(path, encoding='utf-8') as f:
        src = f.read()
    out = src

    if 'manifest.json' not in out:
        out = out.replace('</head>', PWA_HEAD + '\n</head>', 1)

    if 'service-worker.js' not in out:
        out = out.replace('</body>', PWA_SW + '\n</body>', 1)

    if out != src:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
        return True
    return False

def main():
    skip = {'index.html', 'recitation.html'}
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixed = 0

    # index.html و recitation.html — PWA فقط
    for special in ['index.html', 'recitation.html']:
        fp = os.path.join(root, special)
        if os.path.isfile(fp):
            if fix_index_recitation(fp):
                print('FIXED (PWA):', special)
                fixed += 1
            else:
                print('OK:', special)

    # باقي ملفات السور — كل التعديلات + PWA
    for fn in sorted(os.listdir(root)):
        if fn.endswith('.html') and fn not in skip:
            fp = os.path.join(root, fn)
            if os.path.isfile(fp):
                if fix_file(fp):
                    print('FIXED:', fn)
                    fixed += 1
                else:
                    print('OK:', fn)

    print(f'Done: {fixed} fixed')

if __name__ == '__main__':
    main()
