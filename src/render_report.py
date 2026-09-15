"""Render the two-page executive HTML from computed results and editorial copy."""
import html
import json
from pathlib import Path
from string import Template

ROOT=Path(__file__).resolve().parents[1]
COLORS={'human':'#176b65','ai':'#6537c3'}


def escape(value):
    return html.escape(str(value),quote=True)


def metric_chart(results):
    metrics=[('dated_promise','Compromiso con fecha'),('next_step_agreed','Siguiente paso acordado'),('relevant_response','Respuesta a objeciones')]
    parts=['<svg class="chart" viewBox="0 0 740 250" role="img" aria-labelledby="chart-title"><title id="chart-title">Tasas por grupo con intervalos de confianza de Wilson del 95%</title>']
    for tick in [0,25,50,75,100]:
        x=220+3.2*tick
        parts.append(f'<line x1="{x}" y1="29" x2="{x}" y2="214" stroke="#e4deeb"/><text x="{x}" y="234" text-anchor="middle" font-size="11" fill="#655d70">{tick}%</text>')
    parts.append('<text x="625" y="16" text-anchor="middle" font-size="11" fill="#655d70">Casos / evaluables · tasa</text>')
    for idx,(key,label) in enumerate(metrics):
        base=49+idx*65
        parts.append(f'<text x="0" y="{base+10}" font-size="13" font-weight="700" fill="#241c33">{label}</text>')
        for offset,group in [(-2,'human'),(20,'ai')]:
            data=results['metrics'][key][group]
            if data['rate'] is None:
                continue
            y=base+offset
            low,high=data['wilson_95ci']
            x=220+320*data['rate']; lx=220+320*low; hx=220+320*high
            color=COLORS[group]
            rate_text=f'{100*data["rate"]:.1f}'.replace('.',',')
            parts.extend([f'<line x1="{lx:.2f}" y1="{y}" x2="{hx:.2f}" y2="{y}" stroke="{color}" stroke-width="2"/>',f'<line x1="{lx:.2f}" y1="{y-4}" x2="{lx:.2f}" y2="{y+4}" stroke="{color}"/>',f'<line x1="{hx:.2f}" y1="{y-4}" x2="{hx:.2f}" y2="{y+4}" stroke="{color}"/>',f'<circle cx="{x:.2f}" cy="{y}" r="4" fill="{color}"/>',f'<text x="565" y="{y+4}" font-size="12" fill="{color}">{"H" if group=="human" else "IA"} · {data["events"]}/{data["n"]} · {rate_text} %</text>'])
    parts.append('</svg>')
    return '<div class="chart-scroll" tabindex="0" aria-label="Comparación de tasas; desplazar horizontalmente en pantallas pequeñas">'+''.join(parts)+'</div>'


def main():
    result=json.loads((ROOT/'results/analysis.json').read_text(encoding='utf-8'))
    content=json.loads((ROOT/'results/report_content.json').read_text(encoding='utf-8'))
    values={k:escape(v) for k,v in content.items() if isinstance(v,(str,int,float))}
    values['comparison_chart']=metric_chart(result)
    values['kpis']=''.join(f'<div class="kpi"><span class="label">{escape(k["label"])}</span><span class="value">{escape(k["value"])}</span><span class="detail">{escape(k["detail"])}</span></div>' for k in content['kpis'])
    values['actions']=''.join(f'<article class="action"><span class="number">HALLAZGO {i:02d}</span><h3>{escape(a["title"])}</h3><p>{escape(a["finding"])}</p><p class="do">{escape(a["action"])}</p></article>' for i,a in enumerate(content['actions'],1))
    rows=''.join('<tr>'+''.join(f'<td>{escape(c)}</td>' for c in row)+'</tr>' for row in content['context_rows'])
    values['context_table']='<table><thead><tr><th>Dimensión</th><th>Humanos</th><th>IA</th></tr></thead><tbody>'+rows+'</tbody></table>'
    # Structured paragraphs may contain only escaped editorial text.
    for key in ['context_summary','duration_summary']:
        values[key]=''.join('<p>'+escape(p)+'</p>' for p in content[key])
    template=Template((ROOT/'templates/report.html').read_text(encoding='utf-8'))
    page=template.substitute(values)
    (ROOT/'report.html').write_text(page,encoding='utf-8')
    print('Rendered report.html from computed results and reviewed copy.')


if __name__=='__main__':
    main()
