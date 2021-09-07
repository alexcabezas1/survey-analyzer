# Herramienta para analizar encuestas 
aka: Survey Analyzer tool

Herramienta creada para analizar los resultados de encuestas en Google Forms.  

### Motivación:
Fue creado con la intención de analizar los resultados de nuestra [encuesta](https://docs.google.com/forms/d/e/1FAIpQLScZbhqAyavbsVXji-pV-JDSBxKBeUQ_qzfqHqaIckx_WwpEAQ/viewform) para la materia de Seminario 1 - UADE.

### Requerimientos:
Python 3.8+

## Como se usa:
Usa el argumento -f para proveer el archivo con los resultados de la encuesta. 
<br>
<code>
python3 app.py -f resources/encuesta.csv 
</code>
<br>

Usa el argumento -l para ver una lista de las preguntas y sus posibles respuestas (detectadas de la encuesta). Por cada pregunta y respuesta tendrás un identificador que lo puedes usar para formar los grupos que quieres analizar.
<br>
<code>
python3 app.py -f resources/encuesta.csv -l
</code>
Verás algo como esto:
!Ejemplo del argumento -l](static/argument-list-example.PNG "Lista de preguntas y respuestas posibles detectadas")


Usa el argumento -g para suministrar los grupos de preguntas y respuestas que quieres analizar. Puedes proveer multiples grupos separandolos con un espacio.
<br>
<code>
python3 app.py -g p2:r1,p3:r2,p18:r7,p8:r2 p2:r1,p3:r2,p18:r1,p8:r2 -v -f resources/encuesta.csv
</code>
<br>
También puedes suministrar un archivo con los grupos de preguntas y respuestas. Es de utilidad si son muchos los quieres analizar. El contenido del archivo sería un grupo por línea (una lista de grupos). Puedes ver ejemplos en la carpeta queries.
<br>
<code>
python3 app.py -g @args.txt -v -f resources/encuesta.csv
</code>

Usa el argumento -h para obtener una ayuda rápida de la herramienta.
<br>
<code>
python3 app.py -h
</code>
