import unicodedata
from collections import defaultdict
import random

def procesar_texto(texto):
    """Procesa el texto según los criterios especificados"""
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(char for char in texto if unicodedata.category(char) != 'Mn')
    texto = texto.replace('.', '')
    texto = texto.replace(',', '')
    texto = texto.replace(';', '')
    texto = texto.replace('\n', '')
    texto = texto.replace('\r', '')
    texto = texto.replace(' ', '_')
    return texto

class ModeloNGramaCaracteres:
    """Modelo de n-gramas para caracteres"""

    def __init__(self, n, texto):
        self.n = n
        self.texto = texto
        self.conjuntas = defaultdict(int)  # Cuenta de n-gramas completos
        self.condicionales = defaultdict(lambda: defaultdict(int))  # contexto -> siguiente -> cuenta
        self.contextos_totales = defaultdict(int)  # Total de apariciones de cada contexto

        self._calcular_probabilidades()

    def _calcular_probabilidades(self):
        """Calcula las probabilidades conjuntas y condicionales"""
        for i in range(len(self.texto) - self.n + 1):
            ngrama = self.texto[i:i+self.n]
            self.conjuntas[ngrama] += 1

            if self.n > 1:
                contexto = ngrama[:-1]
                siguiente = ngrama[-1]
                self.condicionales[contexto][siguiente] += 1
                self.contextos_totales[contexto] += 1

        # Total de n-gramas para probabilidades conjuntas
        self.total_ngramas = sum(self.conjuntas.values())

    def prob_conjunta(self, ngrama):
        """Probabilidad conjunta P(ngrama)"""
        return self.conjuntas[ngrama] / self.total_ngramas if self.total_ngramas > 0 else 0

    def prob_condicional(self, contexto, siguiente):
        """Probabilidad condicional P(siguiente | contexto)"""
        if contexto in self.contextos_totales and self.contextos_totales[contexto] > 0:
            return self.condicionales[contexto][siguiente] / self.contextos_totales[contexto]
        return 0

    def generar_texto(self, semilla, longitud=250):
        """Genera texto comenzando con una semilla"""
        if len(semilla) != self.n - 1:
            raise ValueError(f"La semilla debe tener {self.n-1} caracteres")

        resultado = semilla
        contexto_actual = semilla

        for _ in range(longitud):
            if contexto_actual not in self.condicionales:
                # Si no hay contexto, elegir uno aleatorio
                if self.condicionales:
                    contexto_actual = random.choice(list(self.condicionales.keys()))
                else:
                    break

            # Obtener posibles siguientes caracteres y sus probabilidades
            siguientes = self.condicionales[contexto_actual]
            if not siguientes:
                break

            caracteres = list(siguientes.keys())
            frecuencias = list(siguientes.values())

            # Elegir el siguiente carácter según las probabilidades
            siguiente_char = random.choices(caracteres, weights=frecuencias, k=1)[0]
            resultado += siguiente_char

            # Actualizar contexto
            contexto_actual = resultado[-(self.n-1):]

        return resultado

    def get_top_ngramas(self, top_n=10):
        """Obtiene los n-gramas más frecuentes"""
        return sorted(self.conjuntas.items(), key=lambda x: x[1], reverse=True)[:top_n]

class ModeloBigramaPalabras:
    """Modelo de bigramas para palabras"""

    def __init__(self, texto_procesado):
        # Convertir el texto procesado (con _) en lista de palabras
        self.palabras = texto_procesado.split('_')
        self.palabras = [p for p in self.palabras if p]  # Eliminar strings vacíos

        self.bigramas = defaultdict(int)
        self.condicionales = defaultdict(lambda: defaultdict(int))
        self.contextos_totales = defaultdict(int)

        self._calcular_probabilidades()

    def _calcular_probabilidades(self):
        """Calcula probabilidades de bigramas de palabras"""
        for i in range(len(self.palabras) - 1):
            palabra1 = self.palabras[i]
            palabra2 = self.palabras[i + 1]

            bigrama = (palabra1, palabra2)
            self.bigramas[bigrama] += 1
            self.condicionales[palabra1][palabra2] += 1
            self.contextos_totales[palabra1] += 1

        self.total_bigramas = sum(self.bigramas.values())

    def prob_conjunta(self, palabra1, palabra2):
        """P(palabra1, palabra2)"""
        return self.bigramas[(palabra1, palabra2)] / self.total_bigramas if self.total_bigramas > 0 else 0

    def prob_condicional(self, palabra1, palabra2):
        """P(palabra2 | palabra1)"""
        if palabra1 in self.contextos_totales and self.contextos_totales[palabra1] > 0:
            return self.condicionales[palabra1][palabra2] / self.contextos_totales[palabra1]
        return 0

    def generar_texto(self, semilla, longitud=250):
        """Genera texto comenzando con una semilla (lista de palabras)"""
        if isinstance(semilla, str):
            # Si es string con _, dividir en palabras
            palabras_semilla = semilla.split('_')
            palabras_semilla = [p for p in palabras_semilla if p]
        else:
            palabras_semilla = semilla

        resultado = list(palabras_semilla)
        palabra_actual = palabras_semilla[-1] if palabras_semilla else None

        if not palabra_actual or palabra_actual not in self.condicionales:
            # Empezar con una palabra aleatoria del corpus
            palabra_actual = random.choice(list(self.condicionales.keys()))
            resultado = [palabra_actual]

        for _ in range(longitud - len(resultado)):
            if palabra_actual not in self.condicionales:
                break

            siguientes = self.condicionales[palabra_actual]
            if not siguientes:
                break

            palabras = list(siguientes.keys())
            frecuencias = list(siguientes.values())

            siguiente_palabra = random.choices(palabras, weights=frecuencias, k=1)[0]
            resultado.append(siguiente_palabra)
            palabra_actual = siguiente_palabra

        return '_'.join(resultado)

    def get_top_bigramas(self, top_n=10):
        """Obtiene los bigramas más frecuentes"""
        return sorted(self.bigramas.items(), key=lambda x: x[1], reverse=True)[:top_n]

def calcular_metricas_consistencia(texto, modelo_usado, tipo='caracter'):
    """Calcula métricas de consistencia del texto generado"""
    metricas = {}

    # 1. Tasa de repetición (n-gramas de 4 caracteres que se repiten)
    if tipo == 'caracter':
        n = 4
        ngramas = [texto[i:i+n] for i in range(len(texto) - n + 1)]
        total = len(ngramas)
        unicos = len(set(ngramas))
        metricas['tasa_repeticion'] = 1 - (unicos / total) if total > 0 else 0
        metricas['longitud'] = len(texto)
    else:  # palabras
        palabras = texto.split('_')
        palabras = [p for p in palabras if p]
        metricas['num_palabras'] = len(palabras)
        metricas['palabras_unicas'] = len(set(palabras))
        metricas['tasa_repeticion_palabras'] = 1 - (len(set(palabras)) / len(palabras)) if palabras else 0

    return metricas

def main():
    print("="*80)
    print("MODELOS DE N-GRAMAS - TEOREMA DE BAYES")
    print("="*80)

    # Leer el texto procesado
    try:
        with open('output_txt/p.txt', 'r', encoding='utf-8') as f:
            texto_procesado = f.read()
    except FileNotFoundError:
        # Si no existe, procesar el original
        print("Procesando el texto original...")
        with open('input_txt/book.txt', 'r', encoding='utf-8') as f:
            texto_original = f.read()
        texto_procesado = procesar_texto(texto_original)
        with open('output_txt/p.txt', 'w', encoding='utf-8') as f:
            f.write(texto_procesado)

    print(f"\nTexto cargado: {len(texto_procesado)} caracteres")
    print(f"Primeros 100 caracteres: {texto_procesado[:100]}...")
    print()

    # ============================================================
    # 1. MODELOS DE N-GRAMAS DE CARACTERES
    # ============================================================
    print("\n" + "="*80)
    print("1. MODELOS DE N-GRAMAS DE CARACTERES")
    print("="*80)

    modelos_chars = {}
    for n in [2, 3, 4]:
        print(f"\n--- {n}-GRAMA DE CARACTERES ---")
        modelo = ModeloNGramaCaracteres(n, texto_procesado)
        modelos_chars[n] = modelo

        print(f"Total de {n}-gramas únicos: {len(modelo.conjuntas)}")
        print(f"\nTop 10 {n}-gramas más frecuentes:")
        for ngrama, freq in modelo.get_top_ngramas(10):
            prob = modelo.prob_conjunta(ngrama)
            print(f"  '{ngrama}': {freq} veces, P = {prob:.6f}")

        # Ejemplos de probabilidades condicionales
        if n == 2:
            print("\nEjemplos de probabilidades condicionales P(b|a):")
            ejemplos = [('e', 'l'), ('l', '_'), ('_', 'e'), ('a', 's')]
            for ctx, sig in ejemplos:
                if ctx in modelo.condicionales:
                    prob = modelo.prob_condicional(ctx, sig)
                    print(f"  P('{sig}' | '{ctx}') = {prob:.6f}")

    # ============================================================
    # 2. GENERACIÓN CON MODELOS DE CARACTERES
    # ============================================================
    print("\n" + "="*80)
    print("2. GENERACIÓN DE TEXTO CON MODELOS DE CARACTERES")
    print("="*80)

    semillas_chars = {
        2: 'e',
        3: 'el',
        4: 'el_'
    }

    textos_generados_chars = {}

    for n, semilla in semillas_chars.items():
        print(f"\n--- GENERACIÓN CON {n}-GRAMA ---")
        print(f"Semilla: '{semilla}'")

        texto_gen = modelos_chars[n].generar_texto(semilla, longitud=250)
        textos_generados_chars[n] = texto_gen

        # Convertir _ a espacios para visualización
        texto_visual = texto_gen.replace('_', ' ')
        print(f"\nTexto generado ({len(texto_gen)} caracteres):")
        print(texto_visual[:500])

        metricas = calcular_metricas_consistencia(texto_gen, modelos_chars[n], tipo='caracter')
        print(f"\nMétricas:")
        print(f"  Longitud: {metricas['longitud']} caracteres")
        print(f"  Tasa de repetición (4-gramas): {metricas['tasa_repeticion']:.4f}")

    # ============================================================
    # 3. MODELO DE BIGRAMAS DE PALABRAS
    # ============================================================
    print("\n" + "="*80)
    print("3. MODELO DE BIGRAMAS DE PALABRAS")
    print("="*80)

    modelo_palabras = ModeloBigramaPalabras(texto_procesado)

    print(f"\nTotal de palabras: {len(modelo_palabras.palabras)}")
    print(f"Palabras únicas: {len(set(modelo_palabras.palabras))}")
    print(f"Bigramas únicos: {len(modelo_palabras.bigramas)}")

    print(f"\nTop 10 bigramas de palabras más frecuentes:")
    for (p1, p2), freq in modelo_palabras.get_top_bigramas(10):
        prob = modelo_palabras.prob_conjunta(p1, p2)
        print(f"  ('{p1}', '{p2}'): {freq} veces, P = {prob:.6f}")

    print("\nEjemplos de probabilidades condicionales P(palabra2 | palabra1):")
    ejemplos_palabras = [
        ('el', 'principito'),
        ('el', 'rey'),
        ('principito', 'dijo'),
        ('muy', 'bien')
    ]
    for p1, p2 in ejemplos_palabras:
        prob = modelo_palabras.prob_condicional(p1, p2)
        print(f"  P('{p2}' | '{p1}') = {prob:.6f}")

    # ============================================================
    # 4. GENERACIÓN CON MODELO DE PALABRAS
    # ============================================================
    print("\n" + "="*80)
    print("4. GENERACIÓN DE TEXTO CON BIGRAMAS DE PALABRAS")
    print("="*80)

    semillas_palabras = [
        'el_principito',
        'el_rey_hablo_con'
    ]

    for semilla in semillas_palabras:
        print(f"\n--- GENERACIÓN CON SEMILLA: '{semilla}' ---")

        texto_gen = modelo_palabras.generar_texto(semilla, longitud=250)

        # Convertir _ a espacios para visualización
        texto_visual = texto_gen.replace('_', ' ')
        num_palabras = len([p for p in texto_gen.split('_') if p])

        print(f"\nTexto generado ({num_palabras} palabras):")
        print(texto_visual[:800])

        metricas = calcular_metricas_consistencia(texto_gen, modelo_palabras, tipo='palabra')
        print(f"\nMétricas:")
        print(f"  Número de palabras: {metricas['num_palabras']}")
        print(f"  Palabras únicas: {metricas['palabras_unicas']}")
        print(f"  Tasa de repetición: {metricas['tasa_repeticion_palabras']:.4f}")

    # ============================================================
    # 5. COMPARACIÓN DE CONSISTENCIA
    # ============================================================
    print("\n" + "="*80)
    print("5. COMPARACIÓN DE CONSISTENCIA")
    print("="*80)

    print("\n RESUMEN:")
    print("\n2-GRAMAS de caracteres:")
    print("  - Tienden a ser muy 'balbuceados' y poco coherentes")
    print("  - Alta variabilidad pero baja estructura")

    print("\n3-GRAMAS de caracteres:")
    print("  - Equilibrio entre variedad y coherencia")
    print("  - Mantienen patrones silábicos")

    print("\n4-GRAMAS de caracteres:")
    print("  - Más coherentes localmente")
    print("  - Respetan mejor la estructura de palabras")
    print("  - Pueden tener más repeticiones si el corpus es pequeño")

    print("\nBIGRAMAS de palabras:")
    print("  - Producen frases más naturales")
    print("  - La unidad (palabra) es más significativa")
    print("  - Pueden crear combinaciones extrañas con corpus pequeño")
    print("  - Generalmente más legibles y coherentes")

    print("\n" + "="*80)
    print("FIN DEL ANÁLISIS")
    print("="*80)

    # Guardar resultados
    with open('output_txt/resultados_ngramas.txt', 'w', encoding='utf-8') as f:
        f.write("RESULTADOS DE GENERACIÓN CON N-GRAMAS\n")
        f.write("="*80 + "\n\n")

        f.write("MODELOS DE CARACTERES:\n\n")
        for n in [2, 3, 4]:
            f.write(f"\n{n}-GRAMA (semilla: '{semillas_chars[n]}'):\n")
            f.write(textos_generados_chars[n].replace('_', ' '))
            f.write("\n\n" + "-"*80 + "\n")

        f.write("\n\nMODELO DE PALABRAS:\n\n")
        for semilla in semillas_palabras:
            f.write(f"\nSemilla: '{semilla}':\n")
            texto = modelo_palabras.generar_texto(semilla, longitud=250)
            f.write(texto.replace('_', ' '))
            f.write("\n\n" + "-"*80 + "\n")

    print("\nResultados guardados en 'output_txt/resultados_ngramas.txt'")

if __name__ == "__main__":
    main()

