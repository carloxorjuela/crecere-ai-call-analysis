# Rúbrica de extracción v1

Las etiquetas describen conductas observables, no personalidad, emociones inferidas o solvencia. No inferir pago efectivo. Nunca usar el nombre del grupo como evidencia.

## Registro por llamada

| Campo | Valores | Regla |
|---|---|---|
| call_id | ID anónimo del inventario | No publicar nombre del archivo original |
| evaluable | 1 / 0 | Derivado público: dated_promise es determinable (1) o nulo (0). No filtra otras métricas |
| customer_speech | 1 / 0 / null | La transcripción contiene intervención atribuible al interlocutor; no inferir por pausas |
| target_contact | 1 / 0 / null | Confirmación explícita de titular; no es contactabilidad poblacional |
| purpose | collection / reminder / other / unclear | Cobranza o negociación nueva frente a recordatorio de un acuerdo previo |
| explicit_promise | 1 / 0 / null | El cliente acepta pagar; excluir intención vaga y propuesta solo del agente |
| dated_promise | 1 / 0 / null | Aceptación de pago y fecha/plazo concreto en contexto; métrica principal |
| amount_agreed | 1 / 0 / null | Cliente acepta un monto específico; no basta que el agente lo mencione |
| prior_agreement | 1 / 0 / null | Acuerdo existente explícitamente mencionado, sin asumir validez actual |
| objection | 1 / 0 / null | Cliente plantea barrera, desacuerdo, desconfianza o imposibilidad relevante |
| objection_type | lista | liquidity, amount_dispute, distrust, already_paid, timing, channel_issue, wrong_party, other |
| relevant_response | 1 / 0 / null | Con objeción: agente responde específicamente a su contenido; null si no hay objeción o no es evaluable |
| alternative_offered | 1 / 0 / null | Propone solución concreta a barrera, como cuota, plazo o canal alternativo |
| next_step_agreed | 1 / 0 / null | Paso concreto y aceptado (pago, envío de soporte, devolución de llamada); separar de promesa de pago |
| closure_recap | 1 / 0 / null | Recapitula al cierre el acuerdo o siguiente paso; no equivale a aceptación |
| outcome | categoría | dated_promise, undated_promise, follow_up, refusal, already_paid, wrong_number, third_party, voicemail, pending_approval, unclear |
| evidence | texto privado | Fragmento textual por etiqueta crítica, índices de segmentos y notas; datos privados |
| review_status | pending / transcript_reviewed / audio_reviewed | Registrar exactamente el tipo de revisión realizada |

## Distinciones esenciales

- Un recordatorio de pago puede confirmar un acuerdo previo; no presentarlo como conversión de un nuevo deudor.
- “Voy a tratar”, “si consigo” y respuestas condicionales no son promesas firmes.
- “Sí” puede ser aceptación si responde inequívocamente a una propuesta concreta de pago; si también podría ser cortesía o escucha, marcar indeterminado y revisar audio.
- Repetir la misma demanda después de una objeción no es una respuesta pertinente.
- Explicar un canal oficial ante desconfianza sí puede ser una respuesta pertinente, aunque no logre convencer al cliente.
- No construir una puntuación subjetiva de claridad: usar conductas concretas como recapitulación y siguiente paso aceptado.
- El silencio no prueba falta de respuesta hasta revisar si hay pérdida/censura de un canal.

## Control de calidad

Conservar versión del modelo y configuración, texto original, evidencia y cambios de etiqueta. La muestra inicial de archivos cortos se usa para probar ASR y no para estimar resultados. Para auditar etiquetas, seleccionar después una muestra aleatoria estratificada con semilla fija y sumar todos los casos ambiguos/críticos. No afirmar que una revisión automatizada fue realizada por una persona.

## Indicadores literales exploratorios

`src/lexical_features.py` normaliza acentos y detecta cuatro patrones: descuento de 0 %, petición de sí/no, vocabulario jurídico y respuesta genérica sobre dudas. Son presencia textual por llamada, no frecuencia ni evaluación legal. El descuento cero se seleccionó como hallazgo durante la revisión, por lo que su contraste es exploratorio.

`needs_audio_review` identifica incertidumbre o casos críticos para escuchar; no acredita que se hayan revisado. Los nulos se conservan como celdas vacías en CSV. Para respuesta pertinente, null también significa no aplicable cuando no se observó objeción.
