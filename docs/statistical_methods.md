# Métodos y supuestos

- Tasas: número de casos positivos sobre observaciones determinables para cada variable. Los desconocidos se muestran aparte; no aplica queda fuera del denominador condicional.
- Intervalos de tasas: Wilson al 95%. Diferencia IA menos humano: intervalo híbrido de Newcombe con intervalos Wilson no agrupados, sin corrección de continuidad.
- Principal: Fisher bilateral para compromiso explícito con fecha/plazo. No seleccionar pruebas según significación observada.
- Duración: diferencia de medianas en segundos, IC percentil bootstrap de 20.000 réplicas; prueba bilateral por permutación de 19.999 réplicas. La prueba de permutación utiliza intercambiabilidad bajo la hipótesis de misma distribución; no equivale a una prueba aislada de medianas bajo cualquier heterogeneidad.
- Semilla: 20260914. Las muestras se tratan como independientes porque no hay identificadores para agrupar clientes/agentes. Repeticiones no detectables pueden estrechar artificialmente los intervalos.
- Los p-valores secundarios se ajustarán conjuntamente con Holm; el resto de cortes se rotula exploratorio. Los intervalos marginales de 95% no son intervalos simultáneos.
- Sensibilidad principal: desconocidos como negativos y como positivos por grupo; evaluar extremos opuestos para la diferencia. No suponer datos faltantes al azar.
- Contexto: propósitos y acuerdos previos son extraídos de conversación y pueden contener error. Los cortes por contexto ayudan a describir composición, no resuelven selección no observada. No atribuir causalidad.
- Menor duración no demuestra mayor productividad; faltan costos, intentos totales, pagos verificados y seguimiento.

Referencias de implementación:

- [SciPy: Fisher exact](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html).
- [SciPy: permutation_test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).
- [Statsmodels: intervalos de dos proporciones y referencias de Newcombe](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html).
