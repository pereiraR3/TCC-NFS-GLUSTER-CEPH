#!/usr/bin/env python3
import math
import os
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


@dataclass(frozen=True)
class Serie:
    nome: str
    cor: tuple
    valores: dict  # tamanho_gib -> vazao_mib_s


def _carregar_fonte(tamanho, negrito=False):
    base = "/usr/share/fonts/truetype/dejavu"
    caminho = os.path.join(base, "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf")
    try:
        return ImageFont.truetype(caminho, tamanho)
    except OSError:
        return ImageFont.load_default()


def _tamanho_texto(draw, texto, fonte):
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _ler_medias_tempo_real(caminho_xlsx):
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(caminho_xlsx) as z:
        sst_root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        compartilhadas = [t.text for t in sst_root.findall(".//main:si/main:t", ns)]
        planilha_root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))

    linhas = []
    for linha in planilha_root.findall(".//main:sheetData/main:row", ns):
        linha_map = {}
        for celula in linha.findall("main:c", ns):
            ref = celula.get("r")
            if not ref:
                continue
            col = re.sub(r"\d+", "", ref)
            v = celula.find("main:v", ns)
            if v is None or v.text is None:
                continue
            valor = v.text
            if celula.get("t") == "s":
                valor = compartilhadas[int(valor)]
            else:
                valor = float(valor)
            linha_map[col] = valor
        linhas.append(linha_map)

    dados = {}
    for linha in linhas:
        tamanho = linha.get("A")
        tempo_real = linha.get("B")
        if isinstance(tamanho, (int, float)) and isinstance(tempo_real, (int, float)):
            dados[float(tamanho)] = float(tempo_real)
    return dados


def _vazao_mib_s(tamanho_gib, segundos):
    return (tamanho_gib * 1024.0) / segundos


def _desenhar_grafico(caminho_saida, tamanhos, series):
    largura, altura = 1280, 720
    margem_esquerda, margem_direita = 110, 60
    margem_topo, margem_base = 90, 110
    grafico_esquerda = margem_esquerda
    grafico_direita = largura - margem_direita
    grafico_topo = margem_topo
    grafico_base = altura - margem_base

    img = Image.new("RGB", (largura, altura), "white")
    draw = ImageDraw.Draw(img)

    fonte_titulo = _carregar_fonte(24, negrito=True)
    fonte_rotulo = _carregar_fonte(16, negrito=False)
    fonte_tick = _carregar_fonte(14, negrito=False)

    titulo = "Comparativo de Vazão (Throughput)"
    tw, th = _tamanho_texto(draw, titulo, fonte_titulo)
    draw.text(((largura - tw) / 2, 30), titulo, fill="black", font=fonte_titulo)

    # Eixos
    draw.line((grafico_esquerda, grafico_topo, grafico_esquerda, grafico_base), fill="black", width=2)
    draw.line((grafico_esquerda, grafico_base, grafico_direita, grafico_base), fill="black", width=2)

    # Escala Y
    max_val = max(v for s in series for v in s.valores.values())
    passo_y = 100
    y_max = int(math.ceil((max_val * 1.1) / passo_y) * passo_y)

    altura_grafico = grafico_base - grafico_topo
    largura_grafico = grafico_direita - grafico_esquerda

    # Grade + ticks
    cor_grade = (220, 220, 220)
    for y in range(0, y_max + 1, passo_y):
        y_pos = grafico_base - (y / y_max) * altura_grafico
        draw.line((grafico_esquerda, y_pos, grafico_direita, y_pos), fill=cor_grade, width=1)
        rotulo = f"{y}"
        lw, lh = _tamanho_texto(draw, rotulo, fonte_tick)
        draw.text((grafico_esquerda - 10 - lw, y_pos - lh / 2), rotulo, fill="black", font=fonte_tick)

    # Rótulo Y
    rotulo_y = "MiB/s"
    lw, lh = _tamanho_texto(draw, rotulo_y, fonte_rotulo)
    draw.text((20, grafico_topo + (altura_grafico - lh) / 2), rotulo_y, fill="black", font=fonte_rotulo)

    # Rótulos X e barras
    largura_grupo = largura_grafico / len(tamanhos)
    largura_barra = largura_grupo * 0.18
    espacamento = largura_grupo * 0.06

    for i, tamanho in enumerate(tamanhos):
        centro_grupo = grafico_esquerda + largura_grupo * (i + 0.5)
        largura_total_grupo = largura_barra * len(series) + espacamento * (len(series) - 1)
        inicio_x = centro_grupo - largura_total_grupo / 2

        for j, serie in enumerate(series):
            valor = serie.valores.get(tamanho, 0.0)
            altura_barra = (valor / y_max) * altura_grafico
            x0 = inicio_x + j * (largura_barra + espacamento)
            y0 = grafico_base - altura_barra
            x1 = x0 + largura_barra
            y1 = grafico_base
            draw.rectangle((x0, y0, x1, y1), fill=serie.cor)

        rotulo_x = f"{int(tamanho)} GiB"
        lw, lh = _tamanho_texto(draw, rotulo_x, fonte_tick)
        draw.text((centro_grupo - lw / 2, grafico_base + 10), rotulo_x, fill="black", font=fonte_tick)

    # Legenda
    legenda_x = grafico_direita - 200
    legenda_y = grafico_topo + 10
    caixa_legenda = 14
    espaco_legenda = 8
    for idx, serie in enumerate(series):
        y = legenda_y + idx * (caixa_legenda + espaco_legenda)
        draw.rectangle((legenda_x, y, legenda_x + caixa_legenda, y + caixa_legenda), fill=serie.cor)
        draw.text((legenda_x + caixa_legenda + 8, y - 2), serie.nome, fill="black", font=fonte_tick)

    # Rótulo X
    rotulo_x_axis = "Tamanho do Arquivo (GiB)"
    lw, lh = _tamanho_texto(draw, rotulo_x_axis, fonte_rotulo)
    draw.text(((grafico_esquerda + grafico_direita - lw) / 2, altura - lh - 20), rotulo_x_axis, fill="black", font=fonte_rotulo)

    img.save(caminho_saida)


def main():
    base = Path(__file__).resolve().parent

    conjuntos = [
        ("NFS", (31, 119, 180), base / "nfs" / "Média_Resultados_NFS.xlsx"),
        ("GlusterFS", (255, 127, 14), base / "gluster" / "Média_Resultados_Gluster.xlsx"),
        ("CephFS", (44, 160, 44), base / "ceph" / "Média_Resultados_Ceph.xlsx"),
    ]

    series = []
    for nome, cor, caminho in conjuntos:
        tempos_reais = _ler_medias_tempo_real(caminho)
        valores = {tamanho: _vazao_mib_s(tamanho, segundos) for tamanho, segundos in tempos_reais.items()}
        series.append(Serie(nome=nome, cor=cor, valores=valores))

    tamanhos = sorted({tamanho for s in series for tamanho in s.valores.keys()})
    caminho_saida = base / "dashboard.png"
    _desenhar_grafico(str(caminho_saida), tamanhos, series)

    print(f"Gráfico salvo em: {caminho_saida}")


if __name__ == "__main__":
    main()
