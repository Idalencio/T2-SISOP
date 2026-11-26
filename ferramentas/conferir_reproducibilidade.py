"""Confere arquivos protegidos e reproduz os CSVs oficiais numa pasta temporária."""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


def main():
    from experimentos import executar
    from simes.metricas import COLUNAS
    manifesto = json.loads((RAIZ / "resultados/integridade_base.json").read_text(encoding="utf-8"))
    for item in manifesto["arquivos"]:
        atual = hashlib.sha256((RAIZ / item["arquivo"]).read_bytes()).hexdigest()
        if atual != item["sha256"]:
            raise AssertionError("arquivo protegido alterado: " + item["arquivo"])
    comparados = []
    with tempfile.TemporaryDirectory(prefix="simes-reproducao-") as pasta:
        with contextlib.redirect_stdout(io.StringIO()):
            executar(pasta=pasta)
        for nome in COLUNAS:
            esperado = (RAIZ / "resultados" / nome).read_bytes()
            obtido = (Path(pasta) / nome).read_bytes()
            if esperado != obtido:
                raise AssertionError("resultado não reproduzido: " + nome)
            comparados.append(nome)
    resultado = {"arquivos_protegidos_identicos": len(manifesto["arquivos"]),
                 "csvs_reproduzidos_byte_a_byte": comparados, "status": "ok"}
    (RAIZ / "resultados/reproducibilidade.json").write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
