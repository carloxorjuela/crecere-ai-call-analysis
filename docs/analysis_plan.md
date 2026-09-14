# Plan de análisis previo a resultados

Registrado el 14 de septiembre de 2026, antes de transcribir o comparar resultados conversacionales.

## Pregunta
¿Cómo difieren las gestiones humanas y de IA en acuerdos observables, manejo de objeciones y tiempo de llamada dentro de la muestra entregada?

## Unidad y alcance
Una grabación es una observación. Comprobar integridad y duplicados antes de analizar. No se conoce el universo de intentos, la selección de llamadas ni identificadores de clientes/agentes repetidos. Los resultados describen esta muestra; no identifican un efecto causal ni recuperación monetaria efectiva.

## Hipótesis y prioridad
- Principal, bilateral: difiere la proporción de llamadas con compromiso explícito de pago con fecha o plazo concreto. Un asentimiento aislado no cuenta. Fecha propuesta solo por el agente sin aceptación no cuenta.
- Secundaria, bilateral: difiere la duración de las grabaciones.
- Secundaria, bilateral: entre llamadas con objeción evaluable, difiere la proporción con respuesta pertinente a esa objeción.
- Exploratoria: la IA podría mostrar mayor consistencia de cierre y los humanos mayor adaptación ante objeciones. Separar estas exploraciones de las pruebas principales.

## Variables y denominadores
Identificar contacto con interlocutor humano, conversación con destinatario cuando sea verificable, propósito de gestión (cobranza, recordatorio u otro), objeción y categoría, respuesta pertinente, compromiso explícito, fecha/plazo aceptado, monto aceptado, siguiente paso acordado, cierre y duración.

Usar sí/no/no determinable/no aplica según corresponda. No sustituir información desconocida por cero. Cada etiqueta semántica tendrá evidencia textual y, cuando esté disponible, localización temporal. Reportar n/N junto a porcentajes. Resultado principal entre llamadas evaluables, con sensibilidad sobre el total asignando desconocidos a ambos extremos. Contacto observado no equivale a tasa operativa de contactabilidad.

## Extracción y revisión
Procesar ambos grupos con el mismo modelo, configuración y rúbrica. Conservar transcripción y decisiones originales en privado. Revisar una muestra estratificada por grupo y los casos ambiguos/contradictorios; registrar correcciones y limitaciones. La evidencia generada por un modelo debe cotejarse con la transcripción y, para resultados críticos o dudosos, el audio. No presentar acuerdo entre modelos como exactitud humana.

## Estadística
Mostrar recuentos, tasas, diferencia IA menos humano en puntos porcentuales e intervalos de confianza del 95%. Prueba exacta de Fisher para la métrica binaria principal. Para duración, mediana, rango intercuartílico y diferencia de medianas con bootstrap reproducible. Ajustar multiplicidad de pruebas secundarias con Holm si se realizan varias. No interpretar falta de significación como equivalencia.

Comparar contexto/propósito solo cuando sea observable. Estratificar por contextos comparables si hay tamaños suficientes. Una regresión ajustada sería exploratoria y solo se usaría con suficiente información y solapamiento; no incluir conductas posteriores como si fueran confusores previos. Evitar modelos complejos con pocas observaciones/eventos. Documentar cualquier cambio de plan.

## Entrega
HTML autónomo de máximo dos páginas al imprimir, con 3–7 hallazgos respaldados por resultados reales; código y documentación públicos. Excluir audios, transcripciones, identificadores y secretos del repositorio. Publicar únicamente derivados revisados que no expongan datos personales. Nunca inventar resultados para completar el reporte.
