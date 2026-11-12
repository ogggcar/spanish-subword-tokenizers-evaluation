# Evaluación morfológica de tokenizadores de subpalabras en español

Este repositorio contiene el código y los datos de evaluación relacionados con el **capítulo 9 de la tesis doctoral de Óscar García Sierra** y con el [artículo asociado](https://docta.ucm.es/entities/publication/81cba166-925e-4053-9306-05f3dd16b3ea). El estudio compara seis tokenizadores de subpalabras en español: BPE, WordPiece y Unigram, cada uno con vocabularios de 31k y 52k.

## Objetivo del estudio

Evaluar en qué medida el vocabulario y las segmentaciones de un tokenizador de subpalabras para español se corresponden con la estructura morfológica de la lengua. La evaluación considera tres aspectos: **relevancia morfológica**, **coherencia morfológica** y **precisión morfológica**.

## Procedimiento

El procedimiento evalúa los seis tokenizadores guardados en el repositorio:

| Tamaño del vocabulario | BPE | WordPiece | Unigram |
|---|---|---|---|
| 31k | [`subword_tokenizers_31/bpe/`](subword_tokenizers_31/bpe/) | [`subword_tokenizers_31/wordpiece/`](subword_tokenizers_31/wordpiece/) | [`subword_tokenizers_31/unigram/`](subword_tokenizers_31/unigram/) |
| 52k | [`subword_tokenizers_52/bpe/`](subword_tokenizers_52/bpe/) | [`subword_tokenizers_52/wordpiece/`](subword_tokenizers_52/wordpiece/) | [`subword_tokenizers_52/unigram/`](subword_tokenizers_52/unigram/) |

Para cada tokenizador se aplican las tres medidas mediante [`src/morphological_evaluator.py`](src/morphological_evaluator.py):

1. **Relevancia morfológica:** compara los morfemas de referencia con el vocabulario del tokenizador y calcula precisión, exhaustividad (*recall*) y F1 por tipo de morfema.
2. **Coherencia morfológica:** tokeniza palabras que contienen prefijos, raíces, sufijos o clíticos y comprueba si la segmentación conserva el morfema evaluado. Informa proporciones de morfemas en un solo token y de segmentaciones en varios tokens, correctas o incorrectas.
3. **Precisión morfológica:** compara las segmentaciones producidas con segmentaciones de referencia y calcula la proporción de coincidencias exactas.

La lógica auxiliar para cargar datos, calcular métricas y normalizar las segmentaciones está en [`src/utils.py`](src/utils.py). Los tokenizadores guardados en las carpetas anteriores son los modelos que corresponden al estudio. Ejecuta la evaluación completa desde la raíz del repositorio con `python -m src.main` (con las dependencias de [`pyproject.toml`](pyproject.toml) instaladas).

Los resultados se escriben en `results/`. El evaluador carga los conjuntos con sus nombres actuales desde `data/` y combina los JSON de `data/2. morph_coherence/`.

## Conjuntos de datos

Los tres conjuntos de evaluación, con los nombres y ubicaciones actuales de `data/`, son:

| Medida | Datos |
|---|---|
| Relevancia morfológica | [`data/1. morph_relevance.json`](data/1.%20morph_relevance.json) |
| Coherencia morfológica | [`data/2. morph_coherence/`](data/2.%20morph_coherence/), dividido en ficheros JSON por tipo de morfema y partes. También se conserva [`data/2. morph_coherence.json`](data/2.%20morph_coherence.json) en Git LFS. |
| Precisión morfológica | [`data/3. morph_accuracy.json`](data/3.%20morph_accuracy.json) |

Como recursos auxiliares se incluyen las tablas de [`afixes.csv`](data/afixes.csv) y [`clitics.csv`](data/clitics.csv) utilizadas para la construcción del conjunto 2.

## Resultados de la evaluación

Los resultados se generan al ejecutar la evaluación y no están preincluidos en el repositorio:

| Medida | Archivo de resultados esperado |
|---|---|
| Relevancia morfológica | `results/task_1_results.json` — resultados desglosados por tokenizador y tipo de morfema, con precisión, *recall* y F1. |
| Coherencia morfológica | `results/task_2_results.json` — resultados desglosados por tipo de morfema y tokenizador. |
| Precisión morfológica | `results/task_3_results.json` — porcentaje de coincidencias exactas y total de casos por tokenizador. |

El evaluador puede generar `results/task_3_errors.json` con recuentos y ejemplos de error para cada tokenizador. **Por el momento, este repositorio no incluye el análisis de esos errores**; el archivo generado contiene ejemplos y categorías, pero no su interpretación.




## Estructura del repositorio

- [`src/`](src/): implementación de la evaluación.
- [`data/`](data/): conjuntos de evaluación y recursos morfológicos auxiliares.
- [`subword_tokenizers_31/`](subword_tokenizers_31/) y [`subword_tokenizers_52/`](subword_tokenizers_52/): configuraciones y vocabularios de tokenizadores con tamaños de vocabulario de 31k y 52k.
- [`notebooks/Train_your_tokenizer.ipynb`](notebooks/Train_your_tokenizer.ipynb): cuaderno de ejemplo para entrenar un tokenizador.
- [`pyproject.toml`](pyproject.toml) y [`poetry.lock`](poetry.lock): dependencias y configuración del proyecto.
