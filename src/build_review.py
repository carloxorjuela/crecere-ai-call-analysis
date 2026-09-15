"""Private local review page: original audio alongside timestamped ASR and codes."""
import csv
import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


def main():
    inventory={r['call_id']:r for r in csv.DictReader((ROOT/'data/private/inventory.csv').open(encoding='utf-8'))}
    codes={}
    for path in sorted((ROOT/'data/private').glob('annotations_batch*.json')):
        batch=json.loads(path.read_text(encoding='utf-8'))
        for row in batch['rows']:
            value=dict(zip(batch['fields'],row))
            codes[value['call_id']]=value
    overrides=ROOT/'data/private/review_overrides.json'
    if overrides.exists():
        for change in json.loads(overrides.read_text(encoding='utf-8')):
            codes[change['call_id']].update(change['changes'])
    items=[]
    for path in sorted((ROOT/'data/private/transcripts/large-v3-turbo').glob('*.json')):
        transcript=json.loads(path.read_text(encoding='utf-8'))
        cid=transcript['call_id']
        supplement=ROOT/'data/private/transcripts/sensitive'/path.name
        if supplement.exists():
            codes[cid]['sensitive_asr_review']=json.loads(supplement.read_text(encoding='utf-8'))['text']
        source=inventory[cid]['source'].replace('\\','/')
        items.append({'id':cid,'audio':'../../'+quote(source),'segments':transcript['segments'],'codes':codes.get(cid,{})})
    data=json.dumps(items,ensure_ascii=False).replace('</','<\\/')
    page='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Revisión privada de llamadas</title>
<style>body{font:16px/1.5 system-ui;background:#f4f3f7;color:#211d2d;margin:0}main{max-width:1100px;margin:auto;padding:28px}h1{font-size:28px}button,select,textarea{font:inherit;padding:10px;border:1px solid #aaa;border-radius:6px}button{cursor:pointer;background:white;color:#362164}button:focus-visible,select:focus-visible,textarea:focus-visible{outline:3px solid #7450d6}audio{width:100%;margin:18px 0}.grid{display:grid;grid-template-columns:1.2fr 1fr;gap:20px}.panel{background:white;border:1px solid #ddd;padding:18px;border-radius:10px;overflow:auto;max-height:65vh}.seg{display:flex;gap:10px;margin:10px 0}.seg button{font-size:12px;height:40px;white-space:nowrap}pre{white-space:pre-wrap;font:13px/1.5 monospace}textarea{width:95%;min-height:110px}#status{color:#5b426f}@media(max-width:700px){.grid{grid-template-columns:1fr}}</style>
<main><h1>Revisión privada · audios y evidencia</h1><p>Estos archivos contienen información de conversaciones. Esta página funciona localmente. Revisa quién habla, la aceptación del cliente y los pasajes dudosos antes de validar etiquetas.</p><label for="calls">Llamada </label><select id="calls"></select> <button id="prev">Anterior</button> <button id="next">Siguiente</button><audio id="audio" controls preload="none"></audio><div class="grid"><section class="panel" aria-label="Transcripción" id="transcript"></section><section class="panel"><h2>Codificación asistida</h2><pre id="codes"></pre><label for="notes">Notas de tu revisión del audio</label><textarea id="notes" placeholder="Indica la corrección, el minuto y la evidencia. No incluyas nombres ni datos personales."></textarea><p><label><input type="checkbox" id="reviewed"> Escuché y revisé esta grabación</label></p><button id="save">Guardar revisión local</button><p id="status" role="status"></p></section></div><p><button id="download">Descargar mis revisiones</button></p><p>Guardar notas no modifica automáticamente las etiquetas: las correcciones deben incorporarse y el análisis debe volver a ejecutarse.</p></main>
<script>const items=__DATA__;const sel=document.getElementById('calls'),player=document.getElementById('audio');let notes={};try{notes=JSON.parse(localStorage.getItem('crecere-review-v1')||'{}')}catch(e){}for(const x of items){const o=document.createElement('option');o.value=x.id;o.textContent=x.id+(x.codes.needs_audio_review?' · revisar audio':'');sel.append(o)}function show(){const x=items[sel.selectedIndex];if(!x)return;player.src=x.audio;document.getElementById('codes').textContent=JSON.stringify(x.codes,null,2);const box=document.getElementById('transcript');box.replaceChildren();for(const s of x.segments){const d=document.createElement('div');d.className='seg';const b=document.createElement('button');b.textContent=s.start.toFixed(1)+' s';b.setAttribute('aria-label','Reproducir desde '+s.start.toFixed(1)+' segundos');b.onclick=()=>{player.currentTime=s.start;player.play()};const t=document.createElement('span');t.textContent=s.text;d.append(b,t);box.append(d)}document.getElementById('notes').value=notes[x.id]?.notes||'';document.getElementById('reviewed').checked=notes[x.id]?.audio_reviewed||false;document.getElementById('status').textContent=''}sel.onchange=show;document.getElementById('prev').onclick=()=>{sel.selectedIndex=Math.max(0,sel.selectedIndex-1);show()};document.getElementById('next').onclick=()=>{sel.selectedIndex=Math.min(items.length-1,sel.selectedIndex+1);show()};document.getElementById('save').onclick=()=>{notes[sel.value]={notes:document.getElementById('notes').value,audio_reviewed:document.getElementById('reviewed').checked,updated_at:new Date().toISOString()};localStorage.setItem('crecere-review-v1',JSON.stringify(notes));document.getElementById('status').textContent='Revisión guardada en este navegador.'};document.getElementById('download').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(notes,null,2)],{type:'application/json'}));a.download='review_decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};show();</script></html>'''.replace('__DATA__',data)
    target=ROOT/'data/private/review.html'
    target.write_text(page,encoding='utf-8')
    print(f'Review page: {len(items)} transcripts, {len(codes)} coded calls')


if __name__=='__main__':
    main()
