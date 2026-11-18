"""Assemble section10_explainer.html from viz_template.html, the data, the fonts and the Python code."""
import json, base64, re, glob
s = open('viz_template.html').read()
F = '/tmp/fonts'
def font(pkg, name):
    p = glob.glob(f'{F}/fontsource-{pkg}-*/files/{name}')[0]
    return base64.b64encode(open(p, 'rb').read()).decode()
fonts = {'SERIF600': ('source-serif-4', 'source-serif-4-latin-600-normal.woff2'),
         'SERIF600X': ('source-serif-4', 'source-serif-4-latin-ext-600-normal.woff2'),
         'SANS400': ('ibm-plex-sans', 'ibm-plex-sans-latin-400-normal.woff2'),
         'SANS400X': ('ibm-plex-sans', 'ibm-plex-sans-latin-ext-400-normal.woff2'),
         'SANS600': ('ibm-plex-sans', 'ibm-plex-sans-latin-600-normal.woff2'),
         'SANS600X': ('ibm-plex-sans', 'ibm-plex-sans-latin-ext-600-normal.woff2'),
         'SANS400I': ('ibm-plex-sans', 'ibm-plex-sans-latin-400-italic.woff2'),
         'MONO400': ('ibm-plex-mono', 'ibm-plex-mono-latin-400-normal.woff2')}
for k, (pkg, name) in fonts.items():
    s = s.replace(f'__{k}__', font(pkg, name))
chev = '<svg viewBox="0 0 10 10" aria-hidden="true"><path d="M3 1.5 7 5l-4 3.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
chevr = '<svg class="chev" viewBox="0 0 20 20" aria-hidden="true"><path d="M7 4l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
s = s.replace('__CHEVR__', chevr).replace('__CHEV__', chev)
d = json.load(open('/tmp/viz_data.json'))
d['gap_se'] = json.load(open('/tmp/gap_se.json'))
d['err_srb'] = {'d': 0.206, 'se': 0.104}
s = s.replace('__DATA__', json.dumps(d, separators=(',', ':'), ensure_ascii=False))
import markdown
def tex(m):
    t = m.group(1)
    rep = [(r'\left(', '('), (r'\right)', ')'), ('{,}', ','), (r'\hat y', 'ŷ'), (r'\beta', 'β'), (r'\tanh', 'tanh'), (r'\sum', 'Σ')]
    for a, b in rep: t = t.replace(a, b)
    t = re.sub(r'_\{([^}]*)\}', r'<sub>\1</sub>', t); t = re.sub(r'_(\w)', r'<sub>\1</sub>', t)
    t = re.sub(r'\^\{([^}]*)\}', r'<sup>\1</sup>', t); t = re.sub(r'\^(\w)', r'<sup>\1</sup>', t)
    t = re.sub(r'(?<![\w<>/])([a-zA-Z])(?![\w>])', r'<i>\1</i>', t)
    return '<span class="tx">' + t + '</span>'
NB = {}
for c in json.load(open('/tmp/nb_cells.json')):
    if c['t'] == 'md':
        holders = []
        txt = re.sub(r'\$([^$]+)\$', lambda m: (holders.append(tex(m)), f'@@TX{len(holders)-1}@@')[1], c['s'])
        h = markdown.markdown(txt)
        for i, x in enumerate(holders): h = h.replace(f'@@TX{i}@@', x)
        h = h.replace('<a href=', '<a target="_blank" rel="noopener" href=')
        if c['p'] == 'intro':   # the page already carries the title and course line
            h = re.sub(r'<h1>.*?</h1>\s*', '', h); h = re.sub(r'<p><em>GOVT 6039, Section 10.*?</em></p>\s*', '', h)
        NB.setdefault(c['p'], []).append({'t': 'md', 'h': h})
    else:
        NB.setdefault(c['p'], []).append({'t': 'code', 's': c['s']})
s = s.replace('__CODE__', json.dumps(NB, ensure_ascii=False))
s = s.replace('__IPYNB__', json.dumps(open('section10_home.ipynb').read(), ensure_ascii=False))
s = s.replace('__PYFILE__', json.dumps(open('section10_home.py').read(), ensure_ascii=False))
assert '__' not in re.sub(r'__(name|main|file)__', '', s.split('<script>')[0]), 'placeholder left'
open('section10_explainer.html', 'w').write(s)
print(len(s) // 1024, 'KB')
