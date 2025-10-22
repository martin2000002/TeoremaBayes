import re
import random
import unicodedata
from collections import Counter, defaultdict

# --- Cargar y limpiar texto ---
with open("book.txt", "r", encoding="utf-8") as f:
    text = f.read()

# --- Función de limpieza ---
def limpiar_texto(t):
    t = t.lower()
    t = ''.join(c for c in unicodedata.normalize('NFD', t)
                if unicodedata.category(c) != 'Mn')  # quitar tildes
    t = re.sub(r'[^a-zñ\s]', '', t)  # eliminar signos de puntuación
    t = re.sub(r'\s+', ' ', t).strip()  # espacios múltiples -> uno solo
    return t

texto = limpiar_texto(text)
print("Longitud del texto limpio:", len(texto))

# -------------------------------------------------
# FUNCIONES DE PROBABILIDADES Y GENERACIÓN
# -------------------------------------------------

def distribucion_conjunta_condicional(texto, n=2):
    """Devuelve las distribuciones conjunta y condicional para n caracteres."""
    conj = Counter([texto[i:i+n] for i in range(len(texto)-n)])
    total = sum(conj.values())
    p_conjunta = {k: v/total for k, v in conj.items()}

    cond = defaultdict(dict)
    for k, v in conj.items():
        prefijo, sig = k[:-1], k[-1]
        cond[prefijo][sig] = cond[prefijo].get(sig, 0) + v

    # Normalizar condicional
    for prefijo, vals in cond.items():
        total_pref = sum(vals.values())
        for sig in vals:
            cond[prefijo][sig] /= total_pref

    return p_conjunta, cond


# --- Calcular para n=2,3,4 ---
dist2, cond2 = distribucion_conjunta_condicional(texto, 2)
dist3, cond3 = distribucion_conjunta_condicional(texto, 3)
dist4, cond4 = distribucion_conjunta_condicional(texto, 4)

# -------------------------------------------------
# GENERACIÓN DE TEXTO (Opción A: prefijo flexible)
# -------------------------------------------------
def generar_texto(cond, inicio, longitud=250):
    resultado = inicio
    n = len(list(cond.keys())[0])
    prefijo = resultado[-(n-1):]

    # Verificar que el prefijo inicial exista
    if prefijo not in cond:
        posibles = [k for k in cond.keys() if k.startswith(prefijo)]
        if posibles:
            prefijo = random.choice(posibles)
            resultado = prefijo
        else:
            # Escoger prefijo ponderado por frecuencia global
            prefijo = random.choices(
                list(cond.keys()),
                weights=[sum(v.values()) for v in cond.values()]
            )[0]
            resultado = prefijo

    while len(resultado) < longitud:
        if prefijo in cond:
            # Elegir la siguiente letra según P(letra | prefijo)
            sig = random.choices(
                list(cond[prefijo].keys()),
                weights=list(cond[prefijo].values())
            )[0]
            resultado += sig
            prefijo = resultado[-(n-1):]
        else:
            # Buscar prefijo similar o elegir ponderado
            posibles = [k for k in cond.keys() if k.startswith(prefijo)]
            if posibles:
                prefijo = random.choice(posibles)
            else:
                prefijo = random.choices(
                    list(cond.keys()),
                    weights=[sum(v.values()) for v in cond.values()]
                )[0]
            # Continuar desde este nuevo prefijo
            sig = random.choices(
                list(cond[prefijo].keys()),
                weights=list(cond[prefijo].values())
            )[0]
            resultado += sig
            prefijo = resultado[-(n-1):]

    return resultado


# -------------------------------------------------
# PROBABILIDADES CONDICIONALES DE PALABRAS
# -------------------------------------------------
palabras = texto.split()
pares = [(palabras[i], palabras[i+1]) for i in range(len(palabras)-1)]
cont_pares = Counter(pares)
cont_pal = Counter(palabras)

p_pal_cond = defaultdict(dict)
for (w1, w2), c in cont_pares.items():
    p_pal_cond[w1][w2] = c / cont_pal[w1]


def generar_palabras(cond, inicio, longitud=50):
    resultado = inicio.split('_')
    while len(resultado) < longitud:
        pref = resultado[-1]

        if pref in cond:
            # Elegimos la siguiente palabra con probabilidad P(w2 | w1)
            sig = random.choices(
                list(cond[pref].keys()),
                weights=list(cond[pref].values())
            )[0]
            resultado.append(sig)
        else:
            # Intentar buscar prefijos que empiecen igual
            posibles = [k for k in cond.keys() if k.startswith(pref)]
            if posibles:
                pref = random.choice(posibles)
                sig = random.choices(
                    list(cond[pref].keys()),
                    weights=list(cond[pref].values())
                )[0]
                resultado.append(sig)
            else:
                # Elegir un prefijo al azar ponderado por frecuencia global
                pref = random.choices(
                    list(cond.keys()),
                    weights=[sum(v.values()) for v in cond.values()]
                )[0]
                sig = random.choices(
                    list(cond[pref].keys()),
                    weights=list(cond[pref].values())
                )[0]
                resultado.append(sig)

    return ' '.join(resultado)


# -------------------------------------------------
# DEMOSTRACIÓN
# -------------------------------------------------
print("\n--- Texto generado con inicio 'el' ---\n")
print(generar_texto(cond2, "el", 250))

print("\n--- Texto generado con inicio 'el_' ---\n")
print(generar_texto(cond3, "el_", 250))

print("\n--- Texto generado con inicio 'el_p' ---\n")
print(generar_texto(cond4, "el_p", 250))

print("\n--- Texto por palabras: 'el principito' ---\n")
print(generar_palabras(p_pal_cond, "el_principito", 50))

print("\n--- Texto por palabras: 'el rey hablo con' ---\n")
print(generar_palabras(p_pal_cond, "el_rey_hablo_con", 50))

