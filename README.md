# Gestiones de cobranza: humanos e IA

Prueba técnica de Creceré AI · 100 grabaciones suministradas, 50 por grupo.

El entregable ejecutivo es **[report.html](report.html)**: descargar y abrir en un navegador, sin servidor ni conexión. El botón de impresión produce dos páginas A4. El informe distingue compromisos verbales, contexto de gestión y duración; **no mide recaudo efectivo ni demuestra un efecto causal del agente**.

## Resultado en una línea

La brecha de la IA está en el cierre: recapitula en 38 % vs 84 % de los humanos (−46 pp), ofrece alternativas en 55 % vs 90 % (−35 pp) y acuerda un siguiente paso en 47 % vs 78 % (−31 pp); las tres resisten Holm. La diferencia en compromisos con fecha (22 % vs 41 %, p = 0,068) no es concluyente y se reduce a −9,6 pp al comparar solo cobranza: la mitad de las llamadas humanas son recordatorios de acuerdos ya pactados y la IA no tiene ninguno.

## Dónde está cada parte del enunciado

| Sección de la prueba | Informe | Código / documento |
|---|---|---|
| 1 · Preguntas, variables, hipótesis, métodos | Página 1, «Cómo se abordó» | [plan previo](docs/analysis_plan.md), [rúbrica](docs/labeling_guide.md), [decisiones](docs/decisions.md) |
| 2 · Base analítica y descriptivos | Página 1, tabla por dimensión | `src/build_dataset.py` → [data/analytic.csv](data/analytic.csv) |
| 3 · Comparación, explicación, conducta, mejora | Páginas 1–2 | `src/analyze.py`, `src/analyze_duration.py` → `results/` |
| 4 · Hallazgos accionables | Página 2, cinco hallazgos | `src/compose_report.py`, `src/render_report.py` |

## Reproducir el resultado

Python 3.13. Desde la raíz del repositorio:

```sh
python -m venv .venv
# Activar el entorno: Windows .venv\Scripts\Activate.ps1; Linux/macOS source .venv/bin/activate
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests -v
python src/analyze_duration.py
python src/analyze.py
python src/compose_report.py
python src/render_report.py
```

La reproducción pública empieza en **[data/analytic.csv](data/analytic.csv)**, una fila por grabación, indicadores sin texto de conversaciones ni identificadores directos. Los nulos son celdas vacías, no ceros. `results/analysis.json` conserva denominadores, diferencias, intervalos, contrastes y sensibilidades; `results/duration_analysis.json` guarda el análisis de tiempo. `compose_report.py` genera las cifras del texto desde esos resultados. GitHub Actions recalcula el informe y comprueba que no cambie.

## Construcción desde los audios autorizados

```sh
python -m pip install -r requirements.txt
python src/inventory.py
python src/transcribe.py --model large-v3-turbo
# Codificar transcripciones con la rúbrica y guardar lotes privados descritos abajo.
python src/lexical_features.py
python src/build_dataset.py
```

Ubicación esperada: `audios_prueba_data_analyst/audios_humanos_censurados` y `audios_prueba_data_analyst/audios_ia_censurados`. El inventario verifica metadatos y hashes, asigna IDs y conserva el vínculo con originales en privado. ASR local: faster-whisper, español, CPU int8, beam 5, VAD y marcas temporales; se reanuda omitiendo archivos terminados. No se usaron servicios cloud facturables.

La **codificación semántica asistida no es una extracción automática determinista**. Codex leyó las transcripciones y aplicó la [rúbrica](docs/labeling_guide.md), guardando listas `fields` y `rows` en `data/private/annotations_batch*.json`, con evidencia de segmentos y motivos de incertidumbre. Las correcciones se conservan en `review_overrides.json` (`call_id`, `changes`, `reason`). `build_dataset.py` valida coherencia y exporta únicamente indicadores. Repetir esta etapa requiere acceso autorizado al material y una nueva revisión; no se distribuyen audios ni transcripciones porque conservan datos personales.

## Criterio y límites

- [Plan previo](docs/analysis_plan.md): registrado en el primer commit antes de revisar resultados conversacionales; hipótesis principal bilateral de compromiso con fecha.
- [Decisiones](docs/decisions.md) y [procedencia de etiquetas](docs/coding_provenance.md): reglas, aclaraciones y asistencia de IA.
- [Métodos estadísticos](docs/statistical_methods.md): Fisher, intervalos Wilson/Newcombe, bootstrap y permutación de medianas, Holm para las dos secundarias y, aparte, para las diez comparaciones exploratorias.
- [Calidad ASR](docs/asr_quality.md): controles dirigidos y omisiones detectadas; no hay verdad de referencia humana ni validación independiente del audio.

Las grabaciones provienen de campañas y momentos distintos. Propósito se infiere del contenido; no reemplaza metadatos de campaña, asignación, saldo o mora. No conocemos repetición de clientes/agentes ni el universo de intentos. Los intervalos suponen observaciones independientes y no incorporan error de transcripción/codificación. Ausencia de significación no prueba equivalencia.

La métrica de respuesta a objeciones registra **al menos una respuesta específica**, no resolución de todas las objeciones. Los patrones literales y comparaciones por propósito son exploratorios. La revisión independiente de audio permanece pendiente y se declara en el informe; la etiqueta `transcript_reviewed` no significa `audio_reviewed`.

## Auditoría local y presentación

```sh
python src/select_audit.py
python src/build_review.py
```

Generan una cola reproducible (5 llamadas aleatorias por grupo más casos marcados) y `data/private/review.html`: reproductor local, segmentos y notas. Seleccionar una muestra **no significa haberla escuchado**. Las correcciones requieren regenerar base, resultados e informe.

Para verificar diseño e impresión en Windows con Edge instalado:

```sh
python -m pip install -r requirements-dev.txt
python src/check_report.py
```

Comprueba dos páginas A4, sin desbordes verticales ni columnas recortadas en tablas, sin scroll horizontal en móvil y sin errores de consola. Las capturas y el PDF de comprobación quedan en `.cache/report_qa/`, fuera de Git. El entregable solicitado es el HTML. Código sencillo por etapas, sin modelos predictivos ni regresiones que la muestra no justifica.
