# EP001 — Informe de limitaciones y errores detectados

## Resultado
Video vertical 1080×1920, 30 fps, 70 s, H.264, audio AAC. Narración, música y efectos reales (ElevenLabs); 7 escenas con cámara animada, polvo, grano, barridos de luz, tipografía y subtítulos sincronizados con la voz (alineados con Whisper).

## Limitaciones importantes (leer antes de publicar)
1. **Los relojes no son los modelos reales.** Son recreaciones conceptuales generadas con IA, con esfera en blanco. La del "Polaris" es un reloj deportivo genérico y **no se parece al Polaris real**; el "Seamaster" tiene manecillas y bisel que no coinciden con el modelo de producción; el "Reverso" sí conserva su silueta rectangular pero sin marca; el "Submariner" es un buzo vintage genérico. Todo está rotulado como conceptual, pero un espectador especializado notará que no son los relojes reales. Recomendación: sustituir por fotos de prensa oficiales.
2. **Sin material auténtico de personas ni películas.** No hay fotos/clips de Pattinson, Craig, Brosnan, Connery, *Dr. No* ni *The Batman*: no pude obtenerlos de forma legítima y decidí no generar parecidos de personas reales. Esas escenas usan siluetas anónimas, lluvia/ciudad, terraza de época y tipografía (007, 1995, 1962).
3. **Reverso:** el volteo es una rotación genérica de una tarjeta; **no se muestra la mecánica interna**. La cara trasera es un panel de acero genérico, no el fondo real de ningún modelo.
4. **Hechos no verificados por mí** (fuentes originales inaccesibles). Ver `FUENTES_Y_PERMISOS.md`.
5. **Marca Alarion:** solo texto; sin logotipo oficial disponible.
6. Resolución de macros: las imágenes base son 1152×2048; los acercamientos fuertes (hasta ×2,8) quedan algo blandos; el grano ayuda a disimularlo.

## Errores encontrados y corregidos durante la producción
- Imágenes generadas inicialmente en 16:9 (el formato por defecto): regeneradas en 9:16.
- Subtítulos cortados por el borde y palabras sin salto de línea; "JAEGER-LECOULTRE" partido por el guion → corregido.
- Rótulos de marca encima del brazalete → relojes reducidos, rótulos en la zona superior.
- Finale: recortes mal centrados y pregunta sobre el Polaris → rediseñado en tres columnas con iluminación progresiva sincronizada con la voz.
- Whisper transcribe mal algunos nombres ("Jager"); los subtítulos usan el guion correcto y solo toman los tiempos.
- Pico de audio inicial −1,1 dBFS en MP3 (ligeramente sobre el objetivo −1,5): dentro de lo aceptable para redes; ajustar si se exige estricto.

## Zonas seguras
Texto importante dentro de y=270–1500 y márgenes de 64 px. El aviso de IA está en y≈292 y el sello de marca final en y≈1330–1400.

## Reproducir
    cd animations/ep001 && npm install
    ./scripts/mix_audio.sh
    npx remotion render src/index.ts Main out/master_1080.mp4 --crf=16
    npx remotion still src/index.ts Cover out/cover.jpg
