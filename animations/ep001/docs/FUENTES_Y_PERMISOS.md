# EP001 — ¿Qué reloj utilizará el nuevo James Bond? — Fuentes y permisos

Fecha de producción: 2026-11-17. Estado: **primera versión para revisión interna, no lista para publicar** (ver pendientes).

## 1. Afirmaciones del guion y su fuente
Todas proceden de la **investigación editorial aportada por el cliente (corte 16-nov-2026)**. En esta sesión **no pude abrir ninguna de las fuentes originales**
(amazon, press.jaeger-lecoultre.com y gq.com están bloqueadas por la red del entorno y el acceso se rechazó), por lo que **no están verificadas de forma independiente**.

| Afirmación en el video | Fuente declarada por el cliente | Verificada por producción |
|---|---|---|
| Robert Pattinson es oficialmente el nuevo James Bond | Amazon MGM Studios; Reuters; AP; British GQ | No |
| Es embajador de Jaeger-LeCoultre | Comunicado de Jaeger-LeCoultre (septiembre 2026) | No |
| Desde 1995 (GoldenEye) Bond usa Omega | Historial público de Omega / prensa especializada | No (dato histórico ampliamente publicado) |
| Pattinson relacionó un Reverso con su Batman | Entrevista citada por el cliente | No — **revisar cita y fecha exactas** |
| 1962: Sean Connery con Rolex Submariner (ref. 6538) | Prensa especializada | No (dato ampliamente publicado; la ref. 6538 no se menciona en pantalla) |
| "Nada está confirmado sobre su próximo reloj" | Cliente | No |

Encuadre editorial: la elección del reloj es una **hipótesis**; el video lo dice en voz y en pantalla ("HIPÓTESIS EDITORIAL · NADA CONFIRMADO"). No afirma que Omega pierda su asociación con Bond.

## 2. Recursos visuales (todos generados con IA, ninguno es material auténtico)
| Recurso | Origen | Notas |
|---|---|---|
| 10 imágenes `public/img/*.png` (escenarios, silueta anónima, 4 relojes) | Seedream 5 Pro vía ElevenLabs (flow `OphWQ43oXaSC93PcinVE`), 1152×2048 | Sin texto, sin logotipos. **Los relojes son recreaciones conceptuales, no los modelos reales.** Etiquetados en pantalla ("VISUALES CONCEPTUALES GENERADOS CON IA"). |
| Persona en pantalla | Silueta anónima de espaldas, generada | **No representa a ningún actor.** No se usó ningún parecido de Pattinson, Craig, Brosnan ni Connery. |
| `grain.png` | Ruido generado con FFmpeg | — |

Decisión de producción: aunque el cliente autorizó recrear a Pattinson, **no se generaron rostros ni parecidos de personas reales** (uso comercial de una marca, derechos de imagen de terceros). Los planos de actores se sustituyeron por composición original.

## 3. Audio
| Recurso | Origen | Notas |
|---|---|---|
| Narración `narration.mp3` (68,2 s) | ElevenLabs, modelo `eleven_v4`, voz "Japa – Narrador Cinematográfico Profundo" (`ifgQptCyquMG1K4fdoT3`, biblioteca de voces) | **Verificar que el plan de ElevenLabs y la licencia de esa voz de biblioteca permitan uso comercial en publicidad.** |
| Música `music.mp3` (72 s) | ElevenLabs Music v2.5, instrumental original | No imita el tema de James Bond. Verificar términos comerciales del plan. |
| Efectos (tick, impacto, whoosh, agua, volteo de caja) | ElevenLabs Sound Effects v2 | Verificar términos comerciales. |
| Mezcla `mix.mp3` | FFmpeg (`scripts/mix_audio.sh`) | Música con ducking bajo la voz; ≈ −14,7 LUFS. |

## 4. Tipografía
Inter / Inter Display (SIL Open Font License), instaladas en el sistema. Marca "ALARION WATCHES" compuesta **como texto**: no existía archivo de logotipo oficial en la sesión.

## 5. Marcas y nombres a revisar antes de publicar
- Se nombran Omega, Seamaster Diver 300M, Jaeger-LeCoultre, Polaris, Reverso, Rolex, Submariner, James Bond y 007. Se usan **solo como texto nominativo/editorial**, sin logotipos. Confirmar con asesoría legal si el uso en contenido de marca (Alarion) puede sugerir afiliación.
- Alarion Watches no es distribuidor oficial de las marcas citadas: valorar un aviso de no afiliación en la descripción.
- No se usó el logotipo de la pistola de 007 ni la banda sonora de la saga.

## 6. Pendientes de permisos/verificación (bloquean la publicación)
1. Verificar las 5 afirmaciones factuales contra las fuentes originales (especialmente la cita del Reverso).
2. Confirmar licencia comercial de ElevenLabs (voz, música, efectos, imágenes) en el plan usado.
3. Sustituir las recreaciones de relojes por **fotografías de prensa oficiales** (Omega, JLC, Rolex) conforme a sus condiciones, si se quiere mostrar los modelos reales.
4. Revisión legal del uso nominativo de marcas y nombres de personas.
