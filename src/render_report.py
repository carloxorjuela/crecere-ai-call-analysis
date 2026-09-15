"""Render the two-page executive HTML from computed results and editorial copy."""
import html
import json
import math
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
INK, MUTED, GRID = '#241c33', '#655d70', '#e4deeb'
PLOT_WIDTH, PLOT_PAD = 240, 10


def escape(value):
    return html.escape(str(value), quote=True)


def make_scale(intervals):
    """Shared pp axis for every difference plot, in steps of 20 and always including 0."""
    low = min(0, math.floor(min(lo for lo, _ in intervals)/20)*20)
    high = max(20, math.ceil(max(hi for _, hi in intervals)/20)*20)
    to_x = lambda v: PLOT_PAD + (v-low)/(high-low)*(PLOT_WIDTH-2*PLOT_PAD)
    return low, high, to_x


def axis_svg(scale):
    low, high, x = scale
    ticks = ''.join(f'<text x="{x(t):.1f}" y="12" text-anchor="middle">{"+" if t > 0 else ""}{t}</text>'
                    for t in range(low, high+1, 20))
    return (f'<svg class="axis" viewBox="0 0 {PLOT_WIDTH} 16" aria-hidden="true">{ticks}</svg>'
            '<div class="axis-legend"><span>← Humanos más</span><span>IA más →</span></div>')


def difference_svg(scale, difference, ci, significant, label):
    """One forest-plot row: IC 95 % line and a dot, filled when the adjusted p < 0.05."""
    low, high, x = scale
    grid = ''.join(f'<line x1="{x(t):.1f}" y1="0" x2="{x(t):.1f}" y2="24" stroke="{GRID}"/>'
                   for t in range(low, high+1, 20) if t)
    fill = INK if significant else 'white'
    tip = f'{label}: {difference:+.1f} pp, IC 95 % [{ci[0]:.1f}; {ci[1]:.1f}]'.replace('.', ',')
    return (f'<svg class="diff" viewBox="0 0 {PLOT_WIDTH} 24" role="img" aria-label="{escape(tip)}"><title>{escape(tip)}</title>{grid}'
            f'<line x1="{x(0):.1f}" y1="0" x2="{x(0):.1f}" y2="24" stroke="{MUTED}" stroke-dasharray="2 2"/>'
            f'<line x1="{x(ci[0]):.1f}" y1="12" x2="{x(ci[1]):.1f}" y2="12" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
            f'<circle cx="{x(difference):.1f}" cy="12" r="5" fill="{fill}" stroke="{INK}" stroke-width="2"/></svg>')


def kpis_html(kpis):
    return ''.join(
        f'<div class="kpi"><span class="label">{escape(k["label"])}</span>'
        f'<div class="pair"><span><i class="dot human"></i>H <b>{escape(k["human"])}</b></span>'
        f'<span><i class="dot ai"></i>IA <b>{escape(k["ai"])}</b></span></div>'
        f'<span class="detail">{escape(k["detail"])}</span></div>' for k in kpis)


def approach_html(items):
    return ''.join(f'<div class="step"><span class="step-title">{escape(i["title"])}</span><p>{escape(i["text"])}</p></div>' for i in items)


def rate_cell(value):
    return f'<td class="num"><b>{escape(value["rate"])}</b><small>{escape(value["n"])}</small></td>'


def scorecard_html(rows, scale):
    body, previous = [], None
    for r in rows:
        dimension = '' if r['dimension'] == previous else escape(r['dimension'])
        previous = r['dimension']
        tier = ' <span class="tier">principal</span>' if r['tier'] == 'principal' else ''
        body.append(f'<tr class="{"primary" if r["tier"] == "principal" else ""}"><td class="dim">{dimension}</td>'
                    f'<td class="metric">{escape(r["label"])}{tier}</td>{rate_cell(r["human"])}{rate_cell(r["ai"])}<td class="plot">{difference_svg(scale, r["difference_pp"], r["ci_pp"], r["significant"], r["label"])}</td>'
                    f'<td class="num strong">{escape(r["difference"])}</td><td class="num">{escape(r["p"])}</td></tr>')
    head = ('<thead><tr><th>Dimensión</th><th>Métrica</th><th class="num"><i class="dot human"></i>Humanos</th>'
            f'<th class="num"><i class="dot ai"></i>IA</th><th class="plot">{axis_svg(scale)}</th><th class="num">IA − H pp</th><th class="num">p</th></tr></thead>')
    return f'<div class="table-scroll" tabindex="0"><table class="scorecard">{head}<tbody>{"".join(body)}</tbody></table></div>'


def explanation_html(explanation, scale):
    rows = ''.join(f'<tr><td>{escape(a)}</td><td class="num">{escape(h)}</td><td class="num">{escape(i)}</td></tr>'
                   for a, h, i in explanation['rows'])
    gaps = [('Todas las llamadas', explanation['gap_total'], explanation['gap_total_ci']),
            ('Solo cobranza', explanation['gap_collection'], explanation['gap_collection_ci'])]
    plots = ''.join(f'<div class="gap"><span>{label}</span>{difference_svg(scale, d, ci, False, "Compromiso con fecha, " + label.lower())}'
                    f'<b>{format_pp(d)}</b></div>' for label, d, ci in gaps)
    return (f'<table class="compact"><thead><tr><th></th><th class="num"><i class="dot human"></i>H</th><th class="num"><i class="dot ai"></i>IA</th></tr></thead>'
            f'<tbody>{rows}</tbody></table><div class="gaps"><span class="mini-title">Brecha de compromiso IA − H, IC 95 %</span>{plots}</div>'
            f'<p>{escape(explanation["text"])}</p>')


def format_pp(value):
    return (f'{value:.1f}'.replace('.', ',').replace('-', '−')) + ' pp'


def conduct_html(blocks):
    return ''.join(f'<div class="conduct {b["who"]}"><h3>{escape(b["title"])}</h3><ul>'
                   + ''.join(f'<li>{escape(i)}</li>' for i in b['items']) + '</ul></div>' for b in blocks)


def findings_html(findings):
    return ''.join(f'<article class="finding"><div class="big">{escape(f["metric"])}</div><div><span class="number">HALLAZGO {i:02d}</span>'
                   f'<h3>{escape(f["title"])}</h3><p>{escape(f["finding"])}</p><p class="do">→ {escape(f["action"])}</p></div></article>'
                   for i, f in enumerate(findings, 1))


def main():
    content = json.loads((ROOT/'results/report_content.json').read_text(encoding='utf-8'))
    explanation = content['explanation']
    scale = make_scale([r['ci_pp'] for r in content['scorecard']] + [explanation['gap_total_ci'], explanation['gap_collection_ci']])
    values = {k: escape(v) for k, v in content.items() if isinstance(v, str)}
    values.update(
        kpis=kpis_html(content['kpis']),
        approach=approach_html(content['approach']),
        scorecard=scorecard_html(content['scorecard'], scale),
        explanation=explanation_html(explanation, scale),
        conduct=conduct_html(content['conduct']),
        findings=findings_html(content['findings']),
    )
    template = Template((ROOT/'templates/report.html').read_text(encoding='utf-8'))
    (ROOT/'report.html').write_text(template.substitute(values), encoding='utf-8', newline='\n')
    print('Rendered report.html from computed results and reviewed copy.')


if __name__ == '__main__':
    main()
