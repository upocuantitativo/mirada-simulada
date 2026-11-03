"""Prueba el comprobador de narrativa (js/comprobar.js) con informes reales, ejecutándolo en Node.

    python tools/prueba_comprobador.py [fichero.pbix | carpeta_pbip ...]

Sin argumentos analiza el ejemplo MercaSur (página «Antes» y «Después» por separado) y comprueba que
«Antes» suspende y «Después» aprueba. Con argumentos, muestra el resultado de cada informe.
"""
import json, os, subprocess, sys, tempfile, zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")


def ficheros(ruta):
    out = {}
    if os.path.isdir(ruta):
        for d, _, fs in os.walk(ruta):
            for f in fs:
                if f.endswith(".json"):
                    p = os.path.join(d, f)
                    out[os.path.relpath(p, ruta).replace("\\", "/")] = open(p, encoding="utf-8").read()
    else:
        z = zipfile.ZipFile(ruta)
        for n in z.namelist():
            if n == "Report/Layout":
                out[n] = z.read(n).decode("utf-16-le")
            elif n.startswith("Report/definition/") and n.endswith(".json"):
                out[n] = z.read(n).decode("utf-8-sig")
    return out


def analizar(fs):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as t:
        json.dump(fs, t)
    js = ("const C=require(process.argv[1]);const fs=require('fs');"
          "console.log(JSON.stringify(C.analizar(JSON.parse(fs.readFileSync(process.argv[2],'utf8')))))")
    r = subprocess.run(["node", "-e", js, os.path.join(RAIZ, "js", "comprobar.js"), t.name], capture_output=True, text=True, encoding="utf-8")
    os.unlink(t.name)
    if r.returncode:
        raise SystemExit(r.stderr)
    return json.loads(r.stdout)


def mostrar(nombre, a):
    print("\n==", nombre, "|", a.get("formato"), "| nota", a.get("nota"), "|", a.get("valoracion") or a.get("error"))
    for p in a.get("paginas", []):
        print("  ·", p["nombre"], "| nota", p["nota"], "|", p["datos"], "visuales con datos")
        for x in p["reglas"]:
            print("     ", {"cumple": "OK ", "revisar": "?? ", "falla": "MAL"}[x["estado"]], x["id"], x["criterio"], "-", x["evidencia"][:110])
    for x in a.get("informe", []):
        print("    informe:", x["estado"], x["id"], x["evidencia"][:110])


def main():
    if len(sys.argv) > 1:
        for r in sys.argv[1:]:
            mostrar(r, analizar(ficheros(r)))
        return
    base = os.path.join(RAIZ, "ejemplo_mercasur", "MercaSur_Panel", "MercaSur_Panel.Report", "definition")
    todo = ficheros(base)
    res = {}
    for pag in ("antes", "despues"):
        fs = {k: v for k, v in todo.items() if f"pages/{pag}/" in k}
        res[pag] = analizar(fs)
        mostrar(pag, res[pag])
    completo = analizar(todo)
    mostrar("informe completo", completo)
    ok = res["antes"]["nota"] < 5 and res["despues"]["nota"] >= 8 and len(completo["paginas"]) == 2
    print("\nRESULTADO:", "correcto" if ok else "FALLO", f"(antes {res['antes']['nota']} < 5, después {res['despues']['nota']} >= 8)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
