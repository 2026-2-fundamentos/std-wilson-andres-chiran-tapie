import glob
import os
import shutil
import string
import time
from pathlib import Path


# ============================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================

ACTIVITY_FOLDER = Path(__file__).resolve().parents[1]

DATA_FOLDER = ACTIVITY_FOLDER / "data"
INPUT_FOLDER = ACTIVITY_FOLDER / "temp" / "input"
OUTPUT_FOLDER = ACTIVITY_FOLDER / "temp" / "output"
SUBMISSION_FOLDER = ACTIVITY_FOLDER / "submission"


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def prepare_empty_folder(folder):
    """Crea una carpeta si no existe y elimina su contenido."""
    folder.mkdir(parents=True, exist_ok=True)

    for item in folder.iterdir():
        if item.is_file() or item.is_symlink():
            item.unlink()
        elif item.is_dir():
            shutil.rmtree(item)


# ============================================================
# 1. PREPARAR CARPETA DE ENTRADA
# ============================================================

prepare_empty_folder(INPUT_FOLDER)


# ============================================================
# 2. GENERAR COPIAS DE LOS ARCHIVOS DE DATA
# ============================================================

N = 1000

if not DATA_FOLDER.exists():
    raise FileNotFoundError(
        f"No existe la carpeta de datos: {DATA_FOLDER}"
    )

source_files = sorted(
    file for file in DATA_FOLDER.iterdir()
    if file.is_file()
)

if not source_files:
    raise FileNotFoundError(
        f"No hay archivos dentro de: {DATA_FOLDER}"
    )

for file in source_files:
    text = file.read_text(encoding="utf-8")

    filename_without_extension = file.stem

    for i in range(1, N + 1):
        new_filename = f"{filename_without_extension}_{i:05d}.txt"
        destination = INPUT_FOLDER / new_filename

        destination.write_text(text, encoding="utf-8")


# ============================================================
# 3. LECTURA DE LOS ARCHIVOS
# ============================================================

start_time = time.time()

sequence = []

files = sorted(
    file for file in INPUT_FOLDER.iterdir()
    if file.is_file()
)

for file in files:
    with file.open("r", encoding="utf-8") as f:
        for line in f:
            sequence.append((str(file), line))


# ============================================================
# 4. MAPPER: CONTAR CADA PALABRA
# ============================================================

pairs_sequence = []

for _, line in sequence:
    line = line.lower()
    line = line.translate(
        str.maketrans("", "", string.punctuation)
    )
    line = line.replace("\n", "")

    words = line.split()

    pairs_sequence.extend(
        (word, 1) for word in words
    )


# ============================================================
# 5. SHUFFLE AND SORT: ORDENAR LAS PALABRAS
# ============================================================

pairs_sequence = sorted(pairs_sequence)


# ============================================================
# 6. REDUCER: SUMAR LAS REPETICIONES
# ============================================================

result = []

for key, value in pairs_sequence:
    if result and result[-1][0] == key:
        result[-1] = (
            key,
            result[-1][1] + value
        )
    else:
        result.append((key, value))


# ============================================================
# 7. PREPARAR LA CARPETA DE SALIDA
# ============================================================

prepare_empty_folder(OUTPUT_FOLDER)


# ============================================================
# 8. GUARDAR LOS RESULTADOS
# ============================================================

output_file = OUTPUT_FOLDER / "part-00000"

with output_file.open("w", encoding="utf-8") as f:
    for key, value in result:
        f.write(f"{key}\t{value}\n")


# ============================================================
# 9. CREAR EL MARCADOR DE ÉXITO
# ============================================================

success_file = OUTPUT_FOLDER / "_SUCCESS"
success_file.write_text("", encoding="utf-8")


# ============================================================
# 10. COPIAR LOS RESULTADOS A SUBMISSION
# ============================================================

prepare_empty_folder(SUBMISSION_FOLDER)

for file in OUTPUT_FOLDER.iterdir():
    if file.is_file():
        shutil.copy2(file, SUBMISSION_FOLDER / file.name)


# ============================================================
# 11. REPORTE FINAL
# ============================================================

end_time = time.time()

print("Proceso MapReduce finalizado correctamente.")
print(f"Archivos procesados: {len(files)}")
print(f"Palabras contabilizadas: {sum(value for _, value in result)}")
print(f"Palabras diferentes: {len(result)}")
print(f"Resultados guardados en: {SUBMISSION_FOLDER}")
print(f"Tiempo de ejecución: {end_time - start_time:.2f} segundos")
