import unicodedata
import re

def procesar_texto(texto):
    """
    Procesa el texto según los siguientes criterios:
    - Convierte todo a minúsculas
    - Quita tildes (diacríticos)
    - Elimina puntos, comas, punto y coma y saltos de línea
    - Reemplaza espacios con guion bajo (_)
    """
    # Pasar a minúsculas
    texto = texto.lower()

    # Quitar tildes (normalizar y eliminar diacríticos)
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')

    # Eliminar puntos, comas, punto y coma y saltos de línea
    texto = texto.replace('.', '')
    texto = texto.replace(',', '')
    texto = texto.replace(';', '')
    texto = texto.replace('\n', '')
    texto = texto.replace('\r', '')

    # Reemplazar espacios con guion bajo
    texto = texto.replace(' ', '_')

    return texto

def main():
    # Leer el archivo de entrada
    with open('input_txt/book.txt', 'r', encoding='utf-8') as f:
        texto_original = f.read()

    # Procesar el texto
    texto_procesado = procesar_texto(texto_original)

    # Guardar el resultado en el archivo de salida
    with open('output_txt/p.txt', 'w', encoding='utf-8') as f:
        f.write(texto_procesado)

    print("Texto procesado exitosamente!")
    print(f"Longitud del texto original: {len(texto_original)} caracteres")
    print(f"Longitud del texto procesado: {len(texto_procesado)} caracteres")
    print(f"\nPrimeros 200 caracteres del texto procesado:")
    print(texto_procesado[:200])

if __name__ == "__main__":
    main()

