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

Las tres tareas de evaluación se implementan en [`src/morphological_evaluator.py`](src/morphological_evaluator.py) y corresponden a:

1. **Task 1 — Morphological relevance (relevancia morfológica):** compara los morfemas de referencia con el vocabulario del tokenizador y calcula precisión, exhaustividad (*recall*) y F1 por tipo de morfema.
2. **Task 2 — Morphological coherence (coherencia morfológica):** tokeniza palabras que contienen prefijos, raíces, sufijos o clíticos y comprueba si la segmentación conserva el morfema evaluado. Informa proporciones de morfemas en un solo token y de segmentaciones en varios tokens, correctas o incorrectas.
3. **Task 3 — Morphological accuracy (precisión morfológica):** compara las segmentaciones producidas con segmentaciones de referencia y calcula la proporción de coincidencias exactas.

La lógica auxiliar para cargar datos, calcular métricas y normalizar las segmentaciones está en [`src/utils.py`](src/utils.py). Los tokenizadores guardados en las carpetas anteriores son los modelos que corresponden al estudio.

## Evaluar los tokenizadores del repositorio

Desde la raíz, instala las dependencias y ejecuta la evaluación completa:

```bash
uv sync
uv run python -m src.main
```

La ejecución evalúa los seis tokenizadores locales y escribe sus resultados en `results/task_1_results.json`, `results/task_2_results.json` y `results/task_3_results.json`. El conjunto de coherencia se construye combinando los JSON divididos por tipo de morfema de `data/2. morph_coherence/`.

## Evaluar BETO

Para evaluar BETO ([`dccuchile/bert-base-spanish-wwm-uncased`](https://huggingface.co/dccuchile/bert-base-spanish-wwm-uncased)) en las tres tareas sin sobrescribir los resultados de los tokenizadores del repositorio, ejecuta desde la raíz:

```bash
uv run python -m src.evaluate_beto
```

La primera ejecución descarga el tokenizador desde Hugging Face. Se generan `results/task_1_beto_results.json`, `results/task_2_beto_results.json` y `results/task_3_beto_results.json`.

## Conjuntos de datos

Los tres conjuntos de evaluación, con los nombres y ubicaciones actuales de `data/`, son:

| Medida | Datos |
|---|---|
| Relevancia morfológica | [`data/1. morph_relevance.json`](data/1.%20morph_relevance.json) |
| Coherencia morfológica | [`data/2. morph_coherence/`](data/2.%20morph_coherence/), dividido en ficheros JSON por tipo de morfema y partes. El evaluador combina estos ficheros al ejecutarse; no se necesita un JSON agregado. |
| Precisión morfológica | [`data/3. morph_accuracy.json`](data/3.%20morph_accuracy.json) |

Como recursos auxiliares se incluyen las tablas de [`afixes.csv`](data/afixes.csv) y [`clitics.csv`](data/clitics.csv) utilizadas para la construcción del conjunto 2.

## Resultados de la evaluación

Los resultados se generan al ejecutar la evaluación y no están preincluidos en el repositorio. Los archivos de resultados principales son:

| Medida | Archivo de resultados esperado |
|---|---|
| Tarea | Tokenizadores del repositorio | BETO |
|---|---|---|
| Task 1 — Relevance | `results/task_1_results.json` — precisión, *recall* y F1 por tipo de morfema. | `results/task_1_beto_results.json` |
| Task 2 — Coherence | `results/task_2_results.json` — resultados por tipo de morfema. | `results/task_2_beto_results.json` |
| Task 3 — Accuracy | `results/task_3_results.json` — coincidencias exactas y total de casos. | `results/task_3_beto_results.json` |

**Solo la task 3 genera un archivo de errores.** Durante la evaluación de accuracy, `eval_task3` en [`src/morphological_evaluator.py`](src/morphological_evaluator.py) escribe `results/task_3_errors.json` para los tokenizadores del repositorio. El script de BETO ejecuta esa misma evaluación y produce `results/task_3_beto_errors.json`. Ambos incluyen recuentos y ejemplos de errores de segmentación (subsegmentación, sobresegmentación, subpalabras de referencia no disponibles y desajustes de límites). Task 1 y task 2 no generan archivos de errores. El repositorio no incluye todavía un análisis interpretativo de esos ejemplos.




## Estructura del repositorio

- [`src/`](src/): implementación de la evaluación.
- [`src/evaluate_beto.py`](src/evaluate_beto.py): script para evaluar BETO en las tareas 1, 2 y 3.
- [`data/`](data/): conjuntos de evaluación y recursos morfológicos auxiliares.
- [`subword_tokenizers_31/`](subword_tokenizers_31/) y [`subword_tokenizers_52/`](subword_tokenizers_52/): configuraciones y vocabularios de tokenizadores con tamaños de vocabulario de 31k y 52k.
- [`notebooks/Train_your_tokenizer.ipynb`](notebooks/Train_your_tokenizer.ipynb): cuaderno de ejemplo para entrenar un tokenizador.
- [`pyproject.toml`](pyproject.toml) y [`poetry.lock`](poetry.lock): dependencias y configuración del proyecto.
