"""Generate executive copy with every reported number sourced from results.

Editorial claims (headline, "who does better") are guarded by assertions:
if recomputed results stop supporting a sentence, composition fails instead
of publishing a stale conclusion.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALPHA = .05

# (dimension from the brief, label, metric key)
SCORECARD = [
    ('Contactabilidad', 'Titular confirmado', 'target_contact'),
    ('Objeciones', 'Plantea objeción', 'objection'),
    ('Manejo de objeciones', 'Responde a objeción', 'relevant_response'),
    ('Manejo de objeciones', 'Ofrece alternativa', 'alternative_offered'),
    ('Negociación', 'Acepta un monto', 'amount_agreed'),
    ('Compromiso de pago', 'Compromiso con fecha', 'dated_promise'),
    ('Resultado', 'Siguiente paso', 'next_step_agreed'),
    ('Claridad', 'Recapitula al cierre', 'closure_recap'),
]


def number(value, digits=1):
    text = f'{abs(value):,.{digits}f}'.replace(',', ' ').replace('.', ',')
    return ('−' if value < 0 and round(abs(value), digits) else '') + text


def pvalue(value):
    return '< 0,001' if value < .001 else '= ' + number(value, 3)


def percent(rate, digits=0):
    return number(100*rate, digits) + ' %'


def share(metric, group):
    d = metric[group]
    return f'{d["events"]}/{d["n"]} · {percent(d["rate"], 1)}'


def interval(values):
    return f'[{number(values[0])}; {number(values[1])}]'


def adjusted_p(result, key):
    """Return (p, tier) following the multiplicity plan for each comparison."""
    if key == 'dated_promise':
        return result['metrics'][key]['comparison']['fisher_two_sided_p'], 'principal'
    if key in result['secondary_holm_pvalues']:
        return result['secondary_holm_pvalues'][key], 'secundaria'
    return result['exploratory_holm_pvalues'][key], 'exploratoria'


# Final outcome of each call, collapsed into the five categories shown in the report.
OUTCOME_GROUPS = [
    ('Promesa con fecha', ['dated_promise']),
    ('Otro avance', ['undated_promise', 'follow_up', 'pending_approval', 'already_paid']),
    ('Rechazo', ['refusal']),
    ('Sin gestión efectiva', ['wrong_number', 'third_party', 'voicemail']),
    ('No determinable', ['unclear']),
]


def outcome_section(result):
    counts = result['outcome_counts']
    groups = [{'label': label, 'human': sum(counts['human'].get(k, 0) for k in keys),
               'ai': sum(counts['ai'].get(k, 0) for k in keys)} for label, keys in OUTCOME_GROUPS]
    by_label = {g['label']: g for g in groups}
    no_contact, undetermined = by_label['Sin gestión efectiva'], by_label['No determinable']
    return {
        'groups': groups,
        'text': (f'{no_contact["ai"]}/50 llamadas de IA terminan sin gestión posible (número equivocado, tercero o buzón) '
                 f'frente a {no_contact["human"]}/50 humanas, y otras {undetermined["ai"]} quedan no determinables.'),
        'caption': 'Una categoría por llamada: desenlace observado, no pago verificado.',
    }


def main():
    result = json.loads((ROOT/'results/analysis.json').read_text(encoding='utf-8'))
    duration = json.loads((ROOT/'results/duration_analysis.json').read_text(encoding='utf-8'))
    m = result['metrics']
    primary = m['dated_promise']['comparison']
    collection = result['within_purpose_exploratory']['collection']
    purpose = result['purpose_counts']
    p_of = lambda key: adjusted_p(result, key)[0]
    diff = lambda key: m[key]['comparison']['difference_pp']
    closing = ['closure_recap', 'alternative_offered', 'next_step_agreed']

    # Guards for the editorial narrative.
    assert all(p_of(k) < ALPHA and diff(k) < 0 for k in closing), 'Closing-gap narrative no longer supported'
    assert primary['fisher_two_sided_p'] >= ALPHA, 'Primary result became significant; rewrite headline'
    assert p_of('duration') >= ALPHA, 'Duration difference became significant; rewrite copy'
    assert purpose['ai'].get('reminder', 0) == 0 and purpose['human']['reminder'] > 0, 'Case-mix narrative changed'
    shrink = collection['comparison']['difference_pp']
    assert abs(shrink) < abs(primary['difference_pp']), 'Within-collection gap no longer smaller'
    favorable_ai = [key for *_, key in SCORECARD if diff(key) > 0 and p_of(key) < ALPHA]
    assert not favorable_ai, 'An outcome now favors AI; update conduct copy'

    scorecard = []
    for dimension, label, key in SCORECARD:
        p, tier = adjusted_p(result, key)
        comp = m[key]['comparison']
        scorecard.append({
            'dimension': dimension, 'label': label, 'tier': tier,
            **{g: {'rate': percent(m[key][g]['rate'], 1), 'n': f'{m[key][g]["events"]}/{m[key][g]["n"]}'} for g in ('human', 'ai')},
            'difference_pp': comp['difference_pp'], 'ci_pp': comp['newcombe_95ci_pp'],
            'difference': number(comp['difference_pp']), 'p': pvalue(p), 'significant': p < ALPHA,
        })

    rate = lambda key, g: percent(m[key][g]['rate'])
    human_median, ai_median = duration['human']['median_seconds'], duration['ai']['median_seconds']
    content = {
        'author': 'Carlos Gutiérrez Orjuela',
        'repository_url': 'https://github.com/carloxorjuela/crecere-ai-call-analysis',
        'headline': 'La brecha de la IA está en el cierre de la conversación',
        'lead': (f'En {sum(result["n_by_group"].values())} grabaciones, los humanos ofrecen más alternativas, acuerdan más '
                 f'siguientes pasos y recapitulan más. La diferencia en compromisos de pago con fecha '
                 f'({number(primary["difference_pp"])} pp) no es estadísticamente concluyente y en parte refleja casos distintos.'),
        'kpis': [
            {'label': 'Compromiso con fecha · hipótesis principal', 'human': rate('dated_promise', 'human'), 'ai': rate('dated_promise', 'ai'),
             'detail': f'{number(primary["difference_pp"])} pp · p {pvalue(primary["fisher_two_sided_p"])} · no concluyente'},
            {'label': 'Siguiente paso acordado', 'human': rate('next_step_agreed', 'human'), 'ai': rate('next_step_agreed', 'ai'),
             'detail': f'{number(diff("next_step_agreed"))} pp · p Holm {pvalue(p_of("next_step_agreed"))}'},
            {'label': 'Recapitula al cierre', 'human': rate('closure_recap', 'human'), 'ai': rate('closure_recap', 'ai'),
             'detail': f'{number(diff("closure_recap"))} pp · p Holm {pvalue(p_of("closure_recap"))}'},
            {'label': 'Duración mediana', 'human': number(human_median, 0) + ' s', 'ai': number(ai_median, 0) + ' s',
             'detail': f'{number(duration["comparison"]["difference_seconds"], 0)} s · p Holm {pvalue(p_of("duration"))} · sin diferencia demostrada'},
        ],
        'approach': [
            {'title': 'Preguntas', 'text': '¿Quién logra más compromisos de pago? ¿En qué conductas difieren humanos e IA? ¿La brecha es del agente o del tipo de caso?'},
            {'title': 'Variables', 'text': 'Por llamada, con evidencia textual: contacto, objeción y respuesta, alternativa, monto, fecha, siguiente paso, cierre, propósito, duración y frases del guion.'},
            {'title': 'Hipótesis', 'text': 'Registrada antes de ver resultados: difieren el compromiso con fecha (principal), la duración y la respuesta a objeciones. Esperábamos IA consistente y humanos adaptativos.'},
            {'title': 'Métodos', 'text': 'Tasas n/N e IC Wilson; diferencias con IC Newcombe; Fisher exacto; bootstrap y permutación (duración); Holm por pruebas múltiples; corte por propósito.'},
        ],
        'scorecard': scorecard,
        'scorecard_caption': ('Punto: diferencia IA − humanos; línea: IC 95 %; relleno: p ajustada < 0,05. '
                              'p: Fisher (principal), Holm (secundarias y exploratorias).'),
        'outcomes': outcome_section(result),
        'explanation': {
            'rows': [
                ['Recordatorio de acuerdo', f'{purpose["human"]["reminder"]}/50', f'{purpose["ai"]["reminder"]}/50'],
                ['Menciona acuerdo previo', share(m['prior_agreement'], 'human'), share(m['prior_agreement'], 'ai')],
                ['Compromiso · todas', share(m['dated_promise'], 'human'), share(m['dated_promise'], 'ai')],
                ['Compromiso · cobranza', share(collection, 'human'), share(collection, 'ai')],
            ],
            'gap_total': primary['difference_pp'], 'gap_total_ci': primary['newcombe_95ci_pp'],
            'gap_collection': shrink, 'gap_collection_ci': collection['comparison']['newcombe_95ci_pp'],
            'text': (f'{purpose["human"]["reminder"]}/50 llamadas humanas recuerdan un acuerdo ya pactado; la IA, ninguna. Comparando solo '
                     f'cobranza, la brecha pasa de {number(primary["difference_pp"])} a {number(shrink)} pp '
                     f'(IC {interval(collection["comparison"]["newcombe_95ci_pp"])}).'),
        },
        'conduct': [
            {'who': 'human', 'title': 'Humanos hacen mejor', 'items': [
                f'Ofrecen alternativa: {rate("alternative_offered", "human")} vs {rate("alternative_offered", "ai")}',
                f'Acuerdan siguiente paso: {rate("next_step_agreed", "human")} vs {rate("next_step_agreed", "ai")}',
                f'Recapitulan al cierre: {rate("closure_recap", "human")} vs {rate("closure_recap", "ai")}']},
            {'who': 'ai', 'title': 'IA: fortalezas observadas', 'items': [
                f'Guion uniforme: cita consecuencias jurídicas en {rate("legal_terms", "ai")} vs {rate("legal_terms", "human")}',
                'Contacto con titular y duración: sin diferencia demostrada',
                'Ninguna métrica de resultado la favorece en esta muestra']},
            {'who': 'ai', 'title': 'Riesgos del guion IA', 'items': [
                f'Pregunta cerrada «sí o no»: {rate("binary_answer_prompt", "ai")} vs {rate("binary_answer_prompt", "human")}',
                f'Oferta con «descuento del 0 %»: {m["zero_discount_phrase"]["ai"]["events"]}/50 vs {m["zero_discount_phrase"]["human"]["events"]}/50',
                f'Respuesta genérica a dudas: {m["generic_doubt_response"]["ai"]["events"]}/50 vs {m["generic_doubt_response"]["human"]["events"]}/50']},
        ],
        'findings': [
            {'metric': number(diff('closure_recap'), 0) + ' pp', 'title': 'La IA cierra sin recapitular',
             'finding': f'Recapitula en {rate("closure_recap", "ai")} de sus llamadas frente a {rate("closure_recap", "human")} de los humanos; IC 95 % {interval(m["closure_recap"]["comparison"]["newcombe_95ci_pp"])} pp.',
             'action': 'Paso de cierre obligatorio: repetir monto, fecha y canal, y pedir confirmación explícita.'},
            {'metric': number(diff('alternative_offered'), 0) + ' pp', 'title': 'Pocas alternativas ante la objeción',
             'finding': f'La IA ofrece cuota, plazo o canal alternativo en {rate("alternative_offered", "ai")} frente a {rate("alternative_offered", "human")}; IC 95 % {interval(m["alternative_offered"]["comparison"]["newcombe_95ci_pp"])} pp.',
             'action': 'Árbol de alternativas activado por tipo de objeción, empezando por falta de liquidez.'},
            {'metric': number(diff('next_step_agreed'), 0) + ' pp', 'title': 'Llamadas que terminan sin siguiente paso',
             'finding': f'Siguiente paso acordado: IA {rate("next_step_agreed", "ai")} frente a humanos {rate("next_step_agreed", "human")}; IC 95 % {interval(m["next_step_agreed"]["comparison"]["newcombe_95ci_pp"])} pp.',
             'action': 'No terminar sin pago, soporte o recontacto con fecha; medirlo como KPI diario del agente.'},
            {'metric': f'{m["zero_discount_phrase"]["ai"]["events"]}/50', 'title': 'Ofertas que confunden al cliente',
             'finding': (f'La IA ofrece un «descuento del 0 %» en {m["zero_discount_phrase"]["ai"]["events"]}/50 llamadas y responde dudas con una fórmula genérica en '
                         f'{m["generic_doubt_response"]["ai"]["events"]}/50; humanos: {m["zero_discount_phrase"]["human"]["events"]} y {m["generic_doubt_response"]["human"]["events"]}.'),
             'action': 'Validar montos y porcentajes antes de verbalizarlos; con 0 % presentar financiación, no descuento.'},
            {'metric': number(primary['difference_pp'], 0) + ' pp', 'title': 'Compromisos: brecha no concluyente',
             'finding': f'Compromiso con fecha: IA {share(m["dated_promise"], "ai")} frente a humanos {share(m["dated_promise"], "human")}; p {pvalue(primary["fisher_two_sided_p"])}. En cobranza, {number(shrink)} pp.',
             'action': 'Prueba A/B con asignación aleatoria en la misma campaña y etapa; métrica final: pago efectivo a 7 y 30 días.'},
        ],
        'statistics_note': ('Unidad: grabación. Fisher bilateral para la hipótesis principal; IC Wilson/Newcombe; duración con 20 000 bootstrap y 19 999 permutaciones (semilla fija). '
                            'Independencia asumida: no hay identificadores de cliente o agente.'),
        'limits_note': ('Muestra observacional de campañas y momentos distintos; promesas verbales, no pagos. Con indeterminados en extremos opuestos, la brecha principal va de '
                        f'{number(result["principal_difference_missing_bounds_pp"][0])} a {number(result["principal_difference_missing_bounds_pp"][1])} pp. '
                        'Codificación asistida por IA sobre transcripción automática, sin escucha humana independiente; los IC no incluyen ese error.'),
        'validation_note': '100 filas derivadas sin texto ni datos personales; audios y transcripciones fuera del repositorio. CI recalcula el reporte en cada cambio.',
    }
    (ROOT/'results/report_content.json').write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Composed executive copy from complete computed results.')


if __name__ == '__main__':
    main()
