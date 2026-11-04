# -*- coding: utf-8 -*-
"""Dibuja la pieza mejorada a partir de salida/propuesta.json y los datos, con el mismo diseño que la página principal del
proyecto de Power BI. Sirve para el informe y para volver a pasarla por el laboratorio (prueba A/B).

    python tools/dibujar.py salida/propuesta.json

Salida: salida/grafico_despues.png (1280 x 720) y salida/antes_despues.png (las dos piezas, una al lado de la otra).
"""
import csv, json, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from powerbi_pbip import CALC, ENTRADA, FILAS   # mismos datos (entrada/datos.json) y mismas cifras que el proyecto de Power BI


def imagen_antes():
    """La pieza original: la primera imagen de entrada/ que no sea del laboratorio."""
    e = ENTRADA
    ims = sorted(f for f in os.listdir(e) if f.lower().endswith((".png", ".jpg", ".jpeg")) and not f.startswith(("mapa_calor", "recorrido")))
    return os.path.join(e, "grafico_antes.png" if "grafico_antes.png" in ims else ims[0])


def formato(medida, v):
    if medida == "Aumento acumulado":
        return ("+" if v >= 0 else "") + f"{v:,.0f}".replace(",", ".")
    if medida in ("Crecimiento acumulado",):
        return f"{v * 100:.0f} %"
    if isinstance(v, float) and not v.is_integer():
        return f"{v:.1f}".replace(".", ",")
    return f"{v:,.0f}".replace(",", ".")


def main():
    prop = json.load(open(sys.argv[1], encoding="utf-8"))
    sal = os.path.dirname(os.path.abspath(sys.argv[1]))
    A, TXT, GRIS = prop.get("color_acento", "#0F5B78"), "#1F2937", "#475569"
    plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.patch.set_facecolor("white")
    fig.text(0.031, 0.955, prop["titulo"], fontsize=20, fontweight="bold", color=TXT, va="top")
    fig.text(0.031, 0.885, prop.get("subtitulo", ""), fontsize=12, color=GRIS, va="top")
    tj = prop.get("tarjeta", {"medida": "Aumento acumulado", "etiqueta": ""})
    if tj.get("medida") in CALC:
        fig.text(0.031, 0.74, formato(tj["medida"], CALC[tj["medida"]]), fontsize=46, fontweight="bold", color=A, va="center")
    fig.text(0.031, 0.64, tj.get("etiqueta", ""), fontsize=12, color=GRIS, va="top", wrap=True)
    ax = fig.add_axes([0.30, 0.17, 0.66, 0.62])
    x = [a for a, _ in FILAS]; y = [u for _, u in FILAS]
    ax.plot(x, y, color=A, linewidth=3, marker="o", markersize=6)
    for a, u in FILAS:
        ax.annotate(str(u), (a, u), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=10, color="#334155")
    for an in prop.get("anotaciones", []):
        a = int(an["anio"]); u = dict(FILAS).get(a)
        if u is None:
            continue
        ax.annotate(an["texto"], (a, u), textcoords="offset points", xytext=(-10, 42), ha="right", fontsize=10, fontweight="bold", color=A,
                    arrowprops=dict(arrowstyle="-", color=A, lw=1))
    ymax = -(-int(max(y) * 1.1) // 50) * 50
    ax.set_ylim(0, ymax); ax.set_xticks(x); ax.tick_params(colors=GRIS, labelsize=10, length=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#CBD5E1"); ax.set_yticks([])
    fig.text(0.031, 0.05, prop.get("pie", ""), fontsize=9, color=GRIS, va="bottom")
    ruta = os.path.join(sal, "grafico_despues.png")
    fig.savefig(ruta, facecolor="white"); plt.close(fig)
    antes = Image.open(imagen_antes()).convert("RGB")
    despues = Image.open(ruta).convert("RGB")
    h = 720; antes = antes.resize((round(antes.width * h / antes.height), h)); despues = despues.resize((round(despues.width * h / despues.height), h))
    lienzo = Image.new("RGB", (antes.width + despues.width + 40, h + 60), "white")
    lienzo.paste(antes, (0, 60)); lienzo.paste(despues, (antes.width + 40, 60))
    from PIL import ImageDraw, ImageFont
    dib = ImageDraw.Draw(lienzo)
    try:
        f = ImageFont.truetype("segoeuib.ttf", 30)
    except OSError:
        f = ImageFont.load_default()
    dib.text((10, 12), "Antes", fill="#A33A12", font=f); dib.text((antes.width + 50, 12), "Después", fill=A, font=f)
    lienzo.save(os.path.join(sal, "antes_despues.png"))
    print("Imágenes:", ruta, "y", os.path.join(sal, "antes_despues.png"))


if __name__ == "__main__":
    main()
