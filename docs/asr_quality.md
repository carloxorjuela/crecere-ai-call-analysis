# Control de calidad de transcripción

La transcripción no se trata como verdad de referencia. No se dispone de una transcripción humana independiente de las 100 grabaciones.

## Piloto y sensibilidad

1. Piloto técnico: modelo `small` en dos archivos cortos; se detectó omisión de frases respecto a `large-v3-turbo`. No se calculó WER porque no existe texto de referencia validado.
2. Lote principal: `large-v3-turbo`, español, CPU int8, beam size 5, VAD activado y sin condicionar al texto previo. Se conservan segmentos y marcas de tiempo.
3. Revisión dirigida: 12 archivos dirigidos (6 por grupo) con VAD más sensible (umbral 0,15); dos de ellos también sin VAD. No es una muestra aleatoria ni una estimación de la tasa de error del corpus.
4. Se recuperó en una grabación humana un pasaje relevante omitido por el filtro estándar. Dos variantes lo transcribieron de manera consistente. Se registró una corrección en `data/private/review_overrides.json`; sigue pendiente validación humana del audio.
5. La variante sin VAD también generó una frase espuria en un intervalo inicial. Por ello no se incorporan automáticamente todas sus frases a la base. La concordancia entre variantes no se presenta como exactitud frente a verdad de referencia.

## Tratamiento de incertidumbre

- Una afirmación del agente de que existe acuerdo no sustituye aceptación del cliente.
- Se conservan etiquetas desconocidas cuando la evidencia de aceptación está ausente/ambigua y la calidad impide resolverlo.
- La duración corresponde al archivo completo, no a tiempo de conversación sin silencios.
- Los intervalos estadísticos solo reflejan variación de la muestra bajo sus supuestos; no incorporan automáticamente errores de ASR o codificación.
- La página privada `data/private/review.html` permite escuchar y cotejar segmentos, guardar notas locales y exportar revisiones. No marcar `audio_reviewed` sin haber escuchado efectivamente la grabación.

Los audios y textos pueden conservar datos personales pese al nombre “censurados”; permanecen fuera del repositorio público.



El control sensible adicional de `human_045` recuperó una aceptación explícita y permitió conservar su etiqueta de promesa fechada. En `ai_041` recuperó una mención de descuento cero. Los indicadores literales usan la unión del texto principal y el suplemento sensible disponible; esta cobertura adicional no es uniforme en las 100 llamadas.
