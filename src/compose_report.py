"""Generate executive copy with every reported number sourced from results."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def number(value, digits=1):
    return f'{value:.{digits}f}'.replace('.', ',')


def pvalue(value):
    return '< 0,001' if value < .001 else '= ' + number(value, 3)


def rate(metric, group):
    d = metric[group]
    return f'{d["events"]}/{d["n"]} ({number(100*d["rate"])} %)' if d['n'] else 'Sin casos evaluables'


def interval(values):
    return f'[{number(values[0])}; {number(values[1])}]'


def main():
    result = json.loads((ROOT/'results/analysis.json').read_text(encoding='utf-8'))
    duration = json.loads((ROOT/'results/duration_analysis.json').read_text(encoding='utf-8'))
    metrics = result['metrics']
    primary = metrics['dated_promise']
    comp = primary['comparison']
    time = duration['comparison']
    zero = metrics['zero_discount_phrase']
    collection = result['within_purpose_exploratory']['collection']
    purpose = result['purpose_counts']
    unknown = sum(primary[g]['unknown_or_na'] for g in ['human', 'ai'])
    significant = comp['fisher_two_sided_p'] < .05
    primary_claim = ('Hay diferencia observada; falta separar el efecto del contexto.' if significant
                     else 'La diferencia en compromisos con fecha no es estadísticamente concluyente.')
    next_step = metrics['next_step_agreed']['comparison']
    content = {
        'author': 'Carlos Gutiérrez Orjuela',
        'repository_url': 'https://github.com/carloxorjuela/crecere-ai-call-analysis',
        'headline': 'Más compromisos humanos, en gestiones distintas',
        'lead': primary_claim + ' Análisis de 50 grabaciones humanas y 50 de IA; promesas verbales, no pagos verificados.',
        'recommendation': 'Corregir ofertas inconsistentes y evaluar humanos e IA dentro de la misma campaña y etapa, con seguimiento de pagos.',
        'kpis': [
            {'label': 'Grabaciones analizadas', 'value': str(sum(result['n_by_group'].values())), 'detail': '50 por grupo · muestra suministrada'},
            {'label': 'Compromiso con fecha · IA − H', 'value': number(comp['difference_pp']) + ' pp', 'detail': 'IC 95 % ' + interval(comp['newcombe_95ci_pp']) + ' pp'},
            {'label': 'Compromisos no determinables', 'value': str(unknown) + '/100', 'detail': f'Humanos {primary["human"]["unknown_or_na"]} · IA {primary["ai"]["unknown_or_na"]}'},
        ],
        'comparison_caption': ('Puntos: tasas; líneas: IC 95 % marginales. Compromiso: Fisher p ' + pvalue(comp['fisher_two_sided_p']) +
            '. Siguiente paso: diferencia IA − H ' + number(next_step['difference_pp']) + ' pp, p ' + pvalue(next_step['fisher_two_sided_p']) +
            ' (exploratorio). Objeciones: al menos una respuesta específica, no resolución; p ajustado Holm ' + pvalue(result['secondary_holm_pvalues']['relevant_response']) + '.'),
        'context_summary': [f'Recordatorios: {purpose["human"].get("reminder",0)}/50 humanos frente a {purpose["ai"].get("reminder",0)}/50 IA.',
                            'Propósito inferido de la conversación; la mezcla de casos impide atribuir causalmente la diferencia al agente.'],
        'duration_summary': [f'Mediana: {number(duration["human"]["median_seconds"])} s humanos · {number(duration["ai"]["median_seconds"])} s IA.',
                             f'Diferencia: {number(time["difference_seconds"])} s; IC 95 % {interval(time["bootstrap_95ci_seconds"])} s. Holm p {pvalue(result["secondary_holm_pvalues"]["duration"])}; no demuestra ahorro operativo.'],
        'construction_note': 'Inventario y ASR local; codificación asistida con rúbrica y evidencia por segmentos. Fecha exige aceptación del cliente. Cada tasa excluye sus indeterminados; respuesta usa solo llamadas con objeción.',
        'scope_note': 'Muestra observacional seleccionada, sin universo de intentos ni pagos posteriores. Validación humana independiente del audio pendiente; los IC no incorporan errores de transcripción o codificación.',
        'page2_headline': 'Cuatro decisiones para la siguiente iteración',
        'page2_lead': 'Priorizar correcciones observables y una comparación con contexto común antes de escalar por una supuesta ventaja de efectividad.',
        'context_rows': [
            ['Negociación / cobranza nueva', f'{purpose["human"].get("collection",0)}/50', f'{purpose["ai"].get("collection",0)}/50'],
            ['Recordatorio de acuerdo previo', f'{purpose["human"].get("reminder",0)}/50', f'{purpose["ai"].get("reminder",0)}/50'],
            ['Propósito no determinable', f'{purpose["human"].get("unclear",0)}/50', f'{purpose["ai"].get("unclear",0)}/50'],
            ['Compromiso con fecha, solo cobranza', rate(collection,'human'), rate(collection,'ai')],
            ['Frase «descuento del 0 %»', rate(zero,'human'), rate(zero,'ai')],
        ],
        'context_caption': 'Corte por propósito exploratorio; no ajusta campaña, mora o selección. Patrones literales del ASR, con suplementos dirigidos disponibles; presencia por llamada, no frecuencia.',
        'actions': [
            {'title': 'Separar promesa de recaudo',
             'finding': f'Compromiso con fecha: IA {rate(primary,"ai")} frente a humanos {rate(primary,"human")}. Diferencia {number(comp["difference_pp"])} pp; p {pvalue(comp["fisher_two_sided_p"])}.',
             'action': 'Vincular compromisos con pagos efectivos a 7 y 30 días; auditar aceptación y monto antes de registrar acuerdo.'},
            {'title': 'Comparar la misma etapa',
             'finding': 'Dentro de cobranza, diferencia IA − H ' + number(collection['comparison']['difference_pp']) + ' pp; IC 95 % ' + interval(collection['comparison']['newcombe_95ci_pp']) + ' pp.',
             'action': 'Asignar casos comparables por campaña, mora y acuerdo previo; conservar intentos fallidos y tamaño de muestra suficiente.'},
            {'title': 'Bloquear descuentos sin beneficio',
             'finding': f'La frase de descuento cero aparece en {zero["ai"]["events"]}/{zero["ai"]["n"]} llamadas IA y {zero["human"]["events"]}/{zero["human"]["n"]} humanas; Fisher p {pvalue(zero["comparison"]["fisher_two_sided_p"])} (exploratorio).',
             'action': 'Validar porcentaje y aritmética antes de verbalizar la oferta; con 0 %, presentar financiación sin llamarla descuento.'},
            {'title': 'Cerrar con un siguiente paso',
             'finding': 'Paso acordado: IA ' + rate(metrics['next_step_agreed'],'ai') + ' frente a humanos ' + rate(metrics['next_step_agreed'],'human') + '. Diferencia ' + number(next_step['difference_pp']) + ' pp; IC 95 % ' + interval(next_step['newcombe_95ci_pp']) + ' pp (exploratorio).',
             'action': 'Ante una objeción, acordar pago, documento o recontacto; confirmar responsable y plazo antes de cerrar.'},
        ],
        'statistics_note': 'Fisher bilateral principal; IC Wilson/Newcombe. Duración: 20.000 bootstrap y 19.999 permutaciones; semilla fija. Holm para duración y respuesta. Independencia asumida; clientes/agentes repetidos no identificables.',
        'next_measurement': 'Con indeterminados en extremos opuestos, la diferencia de compromiso IA − H va de ' + number(result['principal_difference_missing_bounds_pp'][0]) + ' a ' + number(result['principal_difference_missing_bounds_pp'][1]) + ' pp (sensibilidad, no IC). Faltan pagos y metadatos de asignación.',
        'validation_note': '100 filas derivadas; audios y transcripciones privados. Codificación asistida, sin validación humana independiente.',
    }
    (ROOT/'results/report_content.json').write_text(json.dumps(content,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Composed executive copy from complete computed results.')


if __name__ == '__main__':
    main()
