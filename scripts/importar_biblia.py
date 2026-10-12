#!/usr/bin/env python3
"""Importa una copia HTML pública de Reina-Valera 1909 desde eBible.
No modifica ni reescribe el texto de los capítulos. Fallará si la fuente cambia.
"""
import io, re, zipfile, urllib.request, pathlib, html
from urllib.parse import urljoin

ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://ebible.org/spaRV1909/'
URL=urljoin(BASE,'spaRV1909_html.zip')
BOOKS=[
('Génesis','GEN',50),('Éxodo','EXO',40),('Levítico','LEV',27),('Números','NUM',36),('Deuteronomio','DEU',34),('Josué','JOS',24),('Jueces','JDG',21),('Rut','RUT',4),('1 Samuel','1SA',31),('2 Samuel','2SA',24),('1 Reyes','1KI',22),('2 Reyes','2KI',25),('1 Crónicas','1CH',29),('2 Crónicas','2CH',36),('Esdras','EZR',10),('Nehemías','NEH',13),('Ester','EST',10),('Job','JOB',42),('Salmos','PSA',150),('Proverbios','PRO',31),('Eclesiastés','ECC',12),('Cantar de los Cantares','SNG',8),('Isaías','ISA',66),('Jeremías','JER',52),('Lamentaciones','LAM',5),('Ezequiel','EZK',48),('Daniel','DAN',12),('Oseas','HOS',14),('Joel','JOL',3),('Amós','AMO',9),('Abdías','OBA',1),('Jonás','JON',4),('Miqueas','MIC',7),('Nahum','NAM',3),('Habacuc','HAB',3),('Sofonías','ZEP',3),('Hageo','HAG',2),('Zacarías','ZEC',14),('Malaquías','MAL',4),
('Mateo','MAT',28),('Marcos','MRK',16),('Lucas','LUK',24),('Juan','JHN',21),('Hechos','ACT',28),('Romanos','ROM',16),('1 Corintios','1CO',16),('2 Corintios','2CO',13),('Gálatas','GAL',6),('Efesios','EPH',6),('Filipenses','PHP',4),('Colosenses','COL',4),('1 Tesalonicenses','1TH',5),('2 Tesalonicenses','2TH',3),('1 Timoteo','1TI',6),('2 Timoteo','2TI',4),('Tito','TIT',3),('Filemón','PHM',1),('Hebreos','HEB',13),('Santiago','JAS',5),('1 Pedro','1PE',5),('2 Pedro','2PE',3),('1 Juan','1JN',5),('2 Juan','2JN',1),('3 Juan','3JN',1),('Judas','JUD',1),('Apocalipsis','REV',22)]
assert len(BOOKS)==66 and sum(x[2] for x in BOOKS)==1189

req=urllib.request.Request(URL,headers={'User-Agent':'TextosDeLaBibliaImporter/1.0 (public-domain Bible archival)'})
with urllib.request.urlopen(req,timeout=120) as r:
    data=r.read(45_000_000)
if len(data)>=45_000_000: raise RuntimeError('Archivo demasiado grande')
z=zipfile.ZipFile(io.BytesIO(data))
files={pathlib.PurePosixPath(n).name.lower():n for n in z.namelist() if not n.endswith('/')}
# Haiola exports book/chapter HTML as GEN01.htm, EXO01.htm, etc.
missing=[f'{code}{chapter:0{3 if code=="PSA" else 2}d}.htm' for _,code,n in BOOKS for chapter in range(1,n+1) if f'{code}{chapter:0{3 if code=="PSA" else 2}d}.htm'.lower() not in files]
if missing: raise RuntimeError(f'La fuente no tiene {len(missing)} capítulos esperados. Primeros: {missing[:8]}')

out=ROOT/'biblia'/'rv1909'
out.mkdir(parents=True,exist_ok=True)
for name in z.namelist():
    if name.endswith('/'): continue
    basename=pathlib.PurePosixPath(name).name
    if not basename or basename.startswith('.'):continue
    if not re.fullmatch(r'[\w.-]+',basename):continue
    if basename.lower().endswith(('.htm','.html','.css','.js','.png','.jpg','.jpeg','.gif','.svg','.ico')):
        (out/basename).write_bytes(z.read(name))

style='''<style>body{font-family:Georgia,serif;background:#f7f5ef;color:#1b302d;line-height:1.6;margin:0}header{background:#18322e;color:white;padding:2rem 5%}main{max-width:1000px;margin:auto;padding:2rem 5%}h1{margin:.2rem 0}a{color:#176b64}header a{color:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}.book{background:white;border:1px solid #deded5;border-radius:8px;padding:13px}.book a{font-weight:bold}.book small{display:block;color:#65736e}footer{margin-top:3rem;font-size:.85rem}</style>'''
parts=['<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Biblioteca bíblica | Textos de la Biblia</title><meta name="description" content="Índice de los 66 libros de la Biblia Reina-Valera 1909, con 1189 capítulos para consultar gratuitamente.">',style,'</head><body><header><a href="/">← Textos de la Biblia</a><h1>Biblioteca bíblica</h1><p>Reina-Valera 1909 · 66 libros · 1.189 capítulos</p></header><main><p>Esta edición histórica conserva la ortografía de su tiempo. Los libros deuterocanónicos están pendientes de incorporación y verificación de fuentes.</p>']
for heading,group in [('Antiguo Testamento',BOOKS[:39]),('Nuevo Testamento',BOOKS[39:])]:
    parts.extend([f'<h2>{heading}</h2>','<div class="grid">'])
    for title,code,count in group:
        parts.append(f'<div class="book"><a href="rv1909/{code}01.htm">{html.escape(title)}</a><small>{count} capítulos</small></div>')
    parts.append('</div>')
parts.append('<footer>Fuente: <a href="https://ebible.org/spaRV1909/index.htm">eBible.org · Reina-Valera 1909</a> (dominio público). Las páginas de los capítulos se reproducen sin modificar su texto.</footer></main></body></html>')
(ROOT/'biblia'/'index.html').write_text('\n'.join(parts),encoding='utf-8')
print(f'IMPORTACIÓN COMPLETA: {len(BOOKS)} libros, {sum(x[2] for x in BOOKS)} capítulos, {len(z.namelist())} entradas en origen.')
