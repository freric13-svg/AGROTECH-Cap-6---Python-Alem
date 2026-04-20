#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════╗
║          FarmTech Solutions - Fase 3                                 ║
║          Sistema de Gestão de Perdas na Colheita de Cana-de-Açúcar  ║
║          Disciplina: Computational Thinking with Python              ║
╚══════════════════════════════════════════════════════════════════════╝

Conteúdos contemplados:
  ✅ Cap. 3 - Subalgoritmos: funções e procedimentos com passagem de parâmetros
  ✅ Cap. 4 - Estruturas de dados: lista, tupla, dicionário, tabela de memória
  ✅ Cap. 5 - Manipulação de arquivos: texto (.txt) e JSON (.json)
  ✅ Cap. 6 - Conexão com banco de dados: Oracle (via oracledb)

Contexto do agronegócio:
  As perdas na colheita mecanizada de cana-de-açúcar chegam a 15%,
  enquanto na colheita manual ficam abaixo de 5%. Este sistema permite
  registrar lotes de colheita, calcular perdas estimadas, salvar
  histórico em JSON/TXT e persistir no banco Oracle para auditoria.
"""

import json
import os
import sys
from datetime import datetime, date

# ──────────────────────────────────────────────────────────────────────
# CONSTANTES DO NEGÓCIO (Tuplas - imutáveis por design)
# ──────────────────────────────────────────────────────────────────────
TIPOS_COLHEITA = ("Manual", "Mecanizada")           # Tupla: imutável
FAIXA_PERDA_MANUAL = (0.0, 5.0)                     # Tupla: min/max %
FAIXA_PERDA_MECANIZADA = (5.0, 15.0)                # Tupla: min/max %
PRECO_TONELADA_CANA = 120.00                        # R$/t (referência UNICA)
ESTADOS_VALIDOS = ("SP", "MG", "GO", "MT", "MS", "PR", "RJ", "BA", "AL", "PE")

# ──────────────────────────────────────────────────────────────────────
# TABELA DE MEMÓRIA (Dicionário de Dicionários - estrutura central)
# ──────────────────────────────────────────────────────────────────────
# Funciona como banco em memória enquanto o Oracle não está disponível
tabela_lotes: dict = {}   # { id_lote: { ...campos... } }
proximo_id: int = 1

# ──────────────────────────────────────────────────────────────────────
# HELPERS DE I/O — validação de entrada (Cap. 3: Funções com parâmetros)
# ──────────────────────────────────────────────────────────────────────

def linha(char: str = "─", tamanho: int = 70) -> None:
    """Procedimento: imprime separador visual."""
    print(char * tamanho)


def cabecalho(titulo: str) -> None:
    """Procedimento: imprime cabeçalho padronizado."""
    linha("═")
    print(f"  🌾 {titulo}")
    linha("═")


def pausar() -> None:
    """Procedimento: aguarda o usuário pressionar ENTER."""
    input("\n  Pressione ENTER para continuar...")


def ler_texto(prompt: str, min_len: int = 1, max_len: int = 100) -> str:
    """
    Função com parâmetros: lê e valida string.
    Parâmetros:
        prompt   - mensagem exibida ao usuário
        min_len  - comprimento mínimo aceito
        max_len  - comprimento máximo aceito
    Retorno: string validada
    """
    while True:
        valor = input(prompt).strip()
        if min_len <= len(valor) <= max_len:
            return valor
        print(f"  ⚠  Texto deve ter entre {min_len} e {max_len} caracteres.")


def ler_float(prompt: str, minimo: float = 0.0, maximo: float = 1e9) -> float:
    """
    Função com parâmetros: lê e valida número decimal.
    Retorno: float dentro do intervalo [minimo, maximo]
    """
    while True:
        try:
            valor = float(input(prompt).replace(",", "."))
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  Valor deve estar entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Entrada inválida. Digite um número decimal.")


def ler_int(prompt: str, minimo: int = 0, maximo: int = 10_000) -> int:
    """
    Função com parâmetros: lê e valida inteiro.
    Retorno: int dentro do intervalo [minimo, maximo]
    """
    while True:
        try:
            valor = int(input(prompt))
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  Valor deve estar entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Entrada inválida. Digite um número inteiro.")


def ler_opcao(prompt: str, opcoes_validas: tuple) -> str:
    """
    Função com parâmetros: lê opção de uma tupla válida.
    Parâmetro tupla demonstra uso de estrutura imutável.
    Retorno: string validada
    """
    while True:
        valor = input(prompt).strip().upper()
        if valor in opcoes_validas:
            return valor
        print(f"  ⚠  Opção inválida. Escolha entre: {', '.join(opcoes_validas)}")


def ler_data(prompt: str) -> str:
    """
    Função: lê e valida data no formato dd/mm/aaaa.
    Retorno: string no formato ISO (aaaa-mm-dd) para persistência.
    """
    while True:
        texto = input(prompt).strip()
        try:
            dt = datetime.strptime(texto, "%d/%m/%Y")
            if dt.date() > date.today():
                print("  ⚠  Data não pode ser futura.")
                continue
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            print("  ⚠  Formato inválido. Use dd/mm/aaaa.")


# ──────────────────────────────────────────────────────────────────────
# CÁLCULOS DE NEGÓCIO (Cap. 3: Funções com parâmetros e retorno)
# ──────────────────────────────────────────────────────────────────────

def calcular_perda_estimada(producao_toneladas: float,
                             tipo_colheita: str,
                             percentual_perda: float) -> tuple:
    """
    Função com múltiplos parâmetros e retorno em TUPLA.

    Calcula a perda estimada de cana com base no tipo de colheita.
    Fonte: SOCICANA - perdas mec. até 15%, manual até 5%.

    Parâmetros:
        producao_toneladas - produção bruta informada pelo produtor (t)
        tipo_colheita      - "Manual" ou "Mecanizada"
        percentual_perda   - % de perda aferida no campo

    Retorno (tupla):
        (toneladas_perdidas, valor_perdido_reais, status_perda)
    """
    # Valida faixa típica conforme tipo
    faixa = FAIXA_PERDA_MANUAL if tipo_colheita == "Manual" else FAIXA_PERDA_MECANIZADA

    toneladas_perdidas = producao_toneladas * (percentual_perda / 100)
    valor_perdido = toneladas_perdidas * PRECO_TONELADA_CANA

    # Classificação por quartis da faixa típica para cada tipo
    limite_excelente = faixa[1] * 0.25   # < 25% da faixa típica → EXCELENTE
    limite_bom       = faixa[1] * 0.60   # < 60% da faixa típica → BOM

    if percentual_perda <= limite_excelente:
        status = "EXCELENTE"
    elif percentual_perda <= limite_bom:
        status = "BOM"
    elif percentual_perda <= faixa[1]:
        status = "ATENÇÃO"
    else:
        status = "CRÍTICO"

    return (toneladas_perdidas, valor_perdido, status)


def calcular_area_colhida(comprimento_m: float, largura_m: float) -> float:
    """
    Função: calcula área colhida em hectares.
    Parâmetros: dimensões em metros.
    Retorno: área em hectares (float).
    """
    area_m2 = comprimento_m * largura_m
    return area_m2 / 10_000   # 1 ha = 10.000 m²


def gerar_resumo_lote(lote: dict) -> dict:
    """
    Função: recebe dicionário de lote e retorna dicionário de resumo.
    Demonstra uso de dicionário como parâmetro e retorno.
    """
    toneladas_perdidas, valor_perdido, status = calcular_perda_estimada(
        lote["producao_toneladas"],
        lote["tipo_colheita"],
        lote["percentual_perda"]
    )
    producao_liquida = lote["producao_toneladas"] - toneladas_perdidas

    resumo = {
        "id_lote": lote["id_lote"],
        "fazenda": lote["fazenda"],
        "estado": lote["estado"],
        "data_colheita": lote["data_colheita"],
        "tipo_colheita": lote["tipo_colheita"],
        "area_hectares": round(lote["area_hectares"], 4),
        "producao_bruta_t": round(lote["producao_toneladas"], 2),
        "percentual_perda": round(lote["percentual_perda"], 2),
        "toneladas_perdidas": round(toneladas_perdidas, 2),
        "producao_liquida_t": round(producao_liquida, 2),
        "valor_perdido_R$": round(valor_perdido, 2),
        "status_perda": status,
        "registro_em": lote["registro_em"]
    }
    return resumo


# ──────────────────────────────────────────────────────────────────────
# CRUD — TABELA DE MEMÓRIA (Cap. 4: Dicionário / lista / tupla)
# ──────────────────────────────────────────────────────────────────────

def inserir_lote() -> None:
    """
    Procedimento: coleta dados do usuário, valida e insere na
    tabela de memória (dicionário) e tenta persistir no Oracle.
    """
    global proximo_id
    cabecalho("CADASTRO DE LOTE DE COLHEITA — CANA-DE-AÇÚCAR")

    print("  Informações do Produtor / Fazenda")
    linha("-")
    fazenda = ler_texto("  Nome da fazenda: ", min_len=3, max_len=80)
    estado = ler_opcao(
        f"  Estado ({'/'.join(ESTADOS_VALIDOS)}): ",
        ESTADOS_VALIDOS
    )
    municipio = ler_texto("  Município: ", min_len=3, max_len=60)

    print("\n  Dados da Área Colhida")
    linha("-")
    comprimento = ler_float("  Comprimento do talhão (m): ", 1, 50_000)
    largura     = ler_float("  Largura do talhão (m): ", 1, 50_000)
    area_ha     = calcular_area_colhida(comprimento, largura)
    print(f"  ✅ Área calculada: {area_ha:.4f} ha  ({comprimento:.1f} m × {largura:.1f} m)")

    print("\n  Dados da Colheita")
    linha("-")
    data_colheita = ler_data("  Data da colheita (dd/mm/aaaa): ")

    print(f"  Tipo de colheita:")
    for i, t in enumerate(TIPOS_COLHEITA, 1):
        print(f"    {i} - {t}")
    opc = ler_int("  Opção: ", 1, len(TIPOS_COLHEITA))
    tipo_colheita = TIPOS_COLHEITA[opc - 1]

    producao = ler_float("  Produção bruta estimada (toneladas): ", 0.1, 500_000)

    faixa = FAIXA_PERDA_MANUAL if tipo_colheita == "Manual" else FAIXA_PERDA_MECANIZADA
    print(f"  Referência de perda para colheita {tipo_colheita}: {faixa[0]}% a {faixa[1]}%")
    percentual = ler_float("  Percentual de perda observado (%): ", 0.0, 100.0)

    variedade = ler_texto("  Variedade da cana (ex: RB867515): ", min_len=2, max_len=30)
    observacao = ler_texto("  Observações (ou 'N/A'): ", min_len=1, max_len=200)

    # Monta dicionário do lote
    lote = {
        "id_lote": proximo_id,
        "fazenda": fazenda,
        "estado": estado,
        "municipio": municipio,
        "area_hectares": area_ha,
        "data_colheita": data_colheita,
        "tipo_colheita": tipo_colheita,
        "producao_toneladas": producao,
        "percentual_perda": percentual,
        "variedade": variedade,
        "observacao": observacao,
        "registro_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    tabela_lotes[proximo_id] = lote
    proximo_id += 1

    # Exibe resumo calculado
    resumo = gerar_resumo_lote(lote)
    print("\n  ✅ Lote cadastrado com sucesso!\n")
    exibir_resumo(resumo)

    # Tenta persistir no Oracle
    _tentar_inserir_oracle(lote)


def listar_lotes() -> None:
    """Procedimento: lista todos os lotes da tabela de memória."""
    cabecalho("LISTAGEM DE LOTES CADASTRADOS")

    if not tabela_lotes:
        print("  Nenhum lote cadastrado ainda.")
        return

    # Lista de IDs ordenada
    ids_ordenados: list = sorted(tabela_lotes.keys())

    for id_lote in ids_ordenados:
        lote = tabela_lotes[id_lote]
        resumo = gerar_resumo_lote(lote)
        exibir_resumo(resumo)
        print()


def exibir_resumo(resumo: dict) -> None:
    """
    Procedimento: exibe dicionário de resumo de forma legível.
    Recebe dicionário como parâmetro.
    """
    status_icone = {
        "EXCELENTE": "🟢", "BOM": "🔵", "ATENÇÃO": "🟡", "CRÍTICO": "🔴"
    }
    icone = status_icone.get(resumo.get("status_perda", ""), "⚪")

    linha("-")
    print(f"  ID Lote .......: #{resumo['id_lote']}")
    print(f"  Fazenda .......: {resumo['fazenda']}  ({resumo['estado']})")
    print(f"  Data Colheita .: {resumo['data_colheita']}")
    print(f"  Tipo Colheita .: {resumo['tipo_colheita']}")
    print(f"  Área ..........: {resumo['area_hectares']:.4f} ha")
    print(f"  Produção Bruta : {resumo['producao_bruta_t']:.2f} t")
    print(f"  Perda .........: {resumo['percentual_perda']:.2f}%  "
          f"({resumo['toneladas_perdidas']:.2f} t  |  "
          f"R$ {resumo['valor_perdido_R$']:,.2f})")
    print(f"  Prod. Líquida .: {resumo['producao_liquida_t']:.2f} t")
    print(f"  Status ........: {icone} {resumo['status_perda']}")
    linha("-")


def atualizar_lote() -> None:
    """Procedimento: atualiza percentual de perda e observações de um lote."""
    cabecalho("ATUALIZAÇÃO DE LOTE")

    if not tabela_lotes:
        print("  Nenhum lote cadastrado.")
        return

    listar_lotes()
    id_escolhido = ler_int("  Digite o ID do lote a atualizar: ", 1, proximo_id)

    if id_escolhido not in tabela_lotes:
        print("  ⚠  ID não encontrado.")
        return

    lote = tabela_lotes[id_escolhido]
    print(f"\n  Lote selecionado: {lote['fazenda']} — {lote['data_colheita']}")
    print("  (Apenas percentual de perda e observação podem ser atualizados)")

    faixa = (FAIXA_PERDA_MANUAL if lote["tipo_colheita"] == "Manual"
             else FAIXA_PERDA_MECANIZADA)
    print(f"  Referência: {faixa[0]}% – {faixa[1]}%")

    novo_percentual = ler_float(
        f"  Novo percentual de perda (atual: {lote['percentual_perda']:.2f}%): ",
        0.0, 100.0
    )
    nova_obs = ler_texto(
        f"  Nova observação (atual: {lote['observacao']}): ",
        min_len=1, max_len=200
    )

    tabela_lotes[id_escolhido]["percentual_perda"] = novo_percentual
    tabela_lotes[id_escolhido]["observacao"] = nova_obs
    tabela_lotes[id_escolhido]["atualizado_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n  ✅ Lote atualizado com sucesso!")
    exibir_resumo(gerar_resumo_lote(tabela_lotes[id_escolhido]))


def excluir_lote() -> None:
    """Procedimento: remove lote da tabela de memória por ID."""
    cabecalho("EXCLUSÃO DE LOTE")

    if not tabela_lotes:
        print("  Nenhum lote cadastrado.")
        return

    listar_lotes()
    id_escolhido = ler_int("  Digite o ID do lote a excluir: ", 1, proximo_id)

    if id_escolhido not in tabela_lotes:
        print("  ⚠  ID não encontrado.")
        return

    lote = tabela_lotes[id_escolhido]
    confirma = input(f"\n  ⚠  Confirma exclusão do lote '{lote['fazenda']}'? (S/N): ").strip().upper()
    if confirma == "S":
        del tabela_lotes[id_escolhido]
        print("  ✅ Lote excluído com sucesso!")
    else:
        print("  Exclusão cancelada.")


# ──────────────────────────────────────────────────────────────────────
# RELATÓRIO ANALÍTICO — usa lista de dicionários
# ──────────────────────────────────────────────────────────────────────

def relatorio_analitico() -> None:
    """
    Procedimento: gera relatório consolidado de todos os lotes.
    Demonstra uso de lista, dicionário e funções auxiliares.
    """
    cabecalho("RELATÓRIO ANALÍTICO — PERDAS NA COLHEITA")

    if not tabela_lotes:
        print("  Sem dados para análise.")
        return

    # Constrói lista de resumos
    resumos: list = [gerar_resumo_lote(l) for l in tabela_lotes.values()]

    # Métricas agregadas via funções
    total_lotes       = len(resumos)
    total_producao    = sum(r["producao_bruta_t"] for r in resumos)
    total_perda_t     = sum(r["toneladas_perdidas"] for r in resumos)
    total_perda_rs    = sum(r["valor_perdido_R$"] for r in resumos)
    media_percentual  = sum(r["percentual_perda"] for r in resumos) / total_lotes
    total_area        = sum(r["area_hectares"] for r in resumos)

    # Distribuição por status (dicionário de contagens)
    distribuicao: dict = {}
    for r in resumos:
        s = r["status_perda"]
        distribuicao[s] = distribuicao.get(s, 0) + 1

    # Pior e melhor lote
    pior  = max(resumos, key=lambda r: r["percentual_perda"])
    melhor = min(resumos, key=lambda r: r["percentual_perda"])

    linha("═")
    print("  📊 CONSOLIDADO GERAL")
    linha()
    print(f"  Total de lotes registrados .: {total_lotes}")
    print(f"  Área total colhida .........: {total_area:.2f} ha")
    print(f"  Produção bruta total .......: {total_producao:,.2f} t")
    print(f"  Total perdido (toneladas) ..: {total_perda_t:,.2f} t")
    print(f"  Valor total perdido ........: R$ {total_perda_rs:,.2f}")
    print(f"  Média de perda .............: {media_percentual:.2f}%")
    print()

    print("  📋 DISTRIBUIÇÃO POR STATUS")
    linha()
    for status, qtd in distribuicao.items():
        barra = "█" * qtd
        print(f"  {status:<12} {barra} ({qtd} lote{'s' if qtd > 1 else ''})")
    print()

    print("  🏆 DESTAQUES")
    linha()
    print(f"  Melhor desempenho : {melhor['fazenda']} ({melhor['estado']}) "
          f"— {melhor['percentual_perda']:.2f}% de perda")
    print(f"  Pior desempenho   : {pior['fazenda']} ({pior['estado']}) "
          f"— {pior['percentual_perda']:.2f}% de perda")
    linha("═")


# ──────────────────────────────────────────────────────────────────────
# MANIPULAÇÃO DE ARQUIVOS — Cap. 5
# ──────────────────────────────────────────────────────────────────────

def salvar_json(caminho: str = "data/lotes_cana.json") -> None:
    """
    Procedimento: persiste tabela de memória em arquivo JSON.
    Demonstra manipulação de arquivo JSON com json.dump.
    """
    cabecalho("EXPORTAÇÃO — JSON")

    if not tabela_lotes:
        print("  Sem dados para exportar.")
        return

    os.makedirs(os.path.dirname(caminho), exist_ok=True)

    payload = {
        "meta": {
            "sistema": "FarmTech Solutions — Fase 3",
            "versao": "3.0.0",
            "exportado_em": datetime.now().isoformat(),
            "total_lotes": len(tabela_lotes)
        },
        "lotes": [gerar_resumo_lote(l) for l in tabela_lotes.values()]
    }

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=4)

    print(f"  ✅ Dados exportados para '{caminho}'  ({len(tabela_lotes)} lotes)")


def carregar_json(caminho: str = "data/lotes_cana.json") -> None:
    """
    Procedimento: importa lotes de arquivo JSON para a tabela de memória.
    Demonstra manipulação de arquivo JSON com json.load.
    """
    global proximo_id
    cabecalho("IMPORTAÇÃO — JSON")

    if not os.path.exists(caminho):
        print(f"  Arquivo '{caminho}' não encontrado.")
        return

    with open(caminho, "r", encoding="utf-8") as f:
        payload = json.load(f)

    importados = 0
    for resumo in payload.get("lotes", []):
        id_lote = resumo["id_lote"]
        if id_lote not in tabela_lotes:
            # Reconstrói dicionário de lote a partir do resumo
            tabela_lotes[id_lote] = {
                "id_lote":            resumo["id_lote"],
                "fazenda":            resumo["fazenda"],
                "estado":             resumo["estado"],
                "municipio":          resumo.get("municipio", "N/I"),
                "area_hectares":      resumo["area_hectares"],
                "data_colheita":      resumo["data_colheita"],
                "tipo_colheita":      resumo["tipo_colheita"],
                "producao_toneladas": resumo["producao_bruta_t"],
                "percentual_perda":   resumo["percentual_perda"],
                "variedade":          resumo.get("variedade", "N/I"),
                "observacao":         resumo.get("observacoes", ""),
                "registro_em":        resumo.get("registro_em", "")
            }
            importados += 1
            if id_lote >= proximo_id:
                proximo_id = id_lote + 1

    print(f"  ✅ {importados} lote(s) importado(s) de '{caminho}'.")


def exportar_relatorio_txt(caminho: str = "data/relatorio_perdas.txt") -> None:
    """
    Procedimento: gera relatório em arquivo de texto (.txt).
    Demonstra manipulação de arquivo texto com open/write.
    """
    cabecalho("EXPORTAÇÃO — RELATÓRIO TXT")

    if not tabela_lotes:
        print("  Sem dados para exportar.")
        return

    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    resumos: list = [gerar_resumo_lote(l) for l in tabela_lotes.values()]

    total_perda_rs   = sum(r["valor_perdido_R$"] for r in resumos)
    media_percentual = sum(r["percentual_perda"] for r in resumos) / len(resumos)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  FARMTECH SOLUTIONS — RELATÓRIO DE PERDAS NA COLHEITA DE CANA\n")
        f.write(f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"  Total de lotes: {len(resumos)}\n")
        f.write(f"  Média de perda: {media_percentual:.2f}%\n")
        f.write(f"  Valor total perdido: R$ {total_perda_rs:,.2f}\n\n")

        f.write("-" * 70 + "\n")
        f.write("  DETALHAMENTO POR LOTE\n")
        f.write("-" * 70 + "\n\n")

        for r in resumos:
            f.write(f"  Lote #{r['id_lote']} — {r['fazenda']} ({r['estado']})\n")
            f.write(f"    Colheita : {r['data_colheita']}  [{r['tipo_colheita']}]\n")
            f.write(f"    Área     : {r['area_hectares']:.4f} ha\n")
            f.write(f"    Produção : {r['producao_bruta_t']:.2f} t  "
                    f"(líquida: {r['producao_liquida_t']:.2f} t)\n")
            f.write(f"    Perda    : {r['percentual_perda']:.2f}%  "
                    f"= {r['toneladas_perdidas']:.2f} t  "
                    f"= R$ {r['valor_perdido_R$']:,.2f}\n")
            f.write(f"    Status   : {r['status_perda']}\n\n")

        f.write("=" * 70 + "\n")
        f.write("  Referências: SOCICANA | UNICA | EMBRAPA\n")
        f.write("=" * 70 + "\n")

    print(f"  ✅ Relatório salvo em '{caminho}'")


# ──────────────────────────────────────────────────────────────────────
# CONEXÃO ORACLE — Cap. 6
# ──────────────────────────────────────────────────────────────────────

def _obter_conexao_oracle():
    """
    Função: tenta estabelecer conexão com o banco Oracle.
    Utiliza oracledb (python-oracledb — substituto oficial do cx_Oracle).
    Retorno: objeto connection ou None se falhar.

    Configuração esperada no arquivo oracle_config.json:
    {
        "usuario": "farmtech",
        "senha": "sua_senha",
        "dsn": "localhost:1521/XEPDB1"
    }
    """
    try:
        import oracledb  # pip install oracledb
    except ImportError:
        return None

    config_path = "oracle_config.json"
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        conn = oracledb.connect(
            user=cfg["usuario"],
            password=cfg["senha"],
            dsn=cfg["dsn"]
        )
        return conn
    except Exception:
        return None


def criar_tabela_oracle() -> None:
    """
    Procedimento: cria a tabela LOTES_CANA no Oracle (se não existir).
    DDL compatível com Oracle 19c/21c/23ai.
    """
    ddl = """
    CREATE TABLE LOTES_CANA (
        ID_LOTE           NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        FAZENDA           VARCHAR2(80)     NOT NULL,
        ESTADO            VARCHAR2(2)      NOT NULL,
        MUNICIPIO         VARCHAR2(60),
        AREA_HECTARES     NUMBER(12,4)     NOT NULL,
        DATA_COLHEITA     DATE             NOT NULL,
        TIPO_COLHEITA     VARCHAR2(15)     NOT NULL,
        PRODUCAO_TON      NUMBER(12,2)     NOT NULL,
        PERCENTUAL_PERDA  NUMBER(5,2)      NOT NULL,
        TONELADAS_PERDIDAS NUMBER(12,2),
        VALOR_PERDIDO_RS  NUMBER(14,2),
        STATUS_PERDA      VARCHAR2(12),
        VARIEDADE         VARCHAR2(30),
        OBSERVACAO        VARCHAR2(200),
        REGISTRO_EM       TIMESTAMP        DEFAULT SYSTIMESTAMP
    )
    """
    conn = _obter_conexao_oracle()
    if conn is None:
        print("  ⚠  Banco Oracle não disponível. Tabela não criada.")
        return

    with conn.cursor() as cur:
        try:
            cur.execute(ddl)
            conn.commit()
            print("  ✅ Tabela LOTES_CANA criada no Oracle.")
        except Exception as e:
            if "ORA-00955" in str(e):   # Tabela já existe
                print("  ℹ  Tabela LOTES_CANA já existe no Oracle.")
            else:
                print(f"  ⚠  Erro ao criar tabela: {e}")
    conn.close()


def _tentar_inserir_oracle(lote: dict) -> None:
    """
    Procedimento interno: tenta inserir lote no Oracle.
    Falha silenciosa se banco não disponível (dados ficam na memória/JSON).
    Parâmetro: dicionário de lote.
    """
    conn = _obter_conexao_oracle()
    if conn is None:
        return   # Oracle não configurado — dados mantidos em memória

    toneladas_perdidas, valor_perdido, status = calcular_perda_estimada(
        lote["producao_toneladas"],
        lote["tipo_colheita"],
        lote["percentual_perda"]
    )

    sql = """
    INSERT INTO LOTES_CANA (
        FAZENDA, ESTADO, MUNICIPIO, AREA_HECTARES,
        DATA_COLHEITA, TIPO_COLHEITA, PRODUCAO_TON,
        PERCENTUAL_PERDA, TONELADAS_PERDIDAS, VALOR_PERDIDO_RS,
        STATUS_PERDA, VARIEDADE, OBSERVACAO
    ) VALUES (
        :fazenda, :estado, :municipio, :area,
        TO_DATE(:data, 'YYYY-MM-DD'), :tipo, :producao,
        :percentual, :perdidas, :valor_perdido,
        :status, :variedade, :obs
    )
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, {
                "fazenda":     lote["fazenda"],
                "estado":      lote["estado"],
                "municipio":   lote["municipio"],
                "area":        lote["area_hectares"],
                "data":        lote["data_colheita"],
                "tipo":        lote["tipo_colheita"],
                "producao":    lote["producao_toneladas"],
                "percentual":  lote["percentual_perda"],
                "perdidas":    toneladas_perdidas,
                "valor_perdido": valor_perdido,
                "status":      status,
                "variedade":   lote["variedade"],
                "obs":         lote["observacao"]
            })
            conn.commit()
            print("  🗄️  Lote também persistido no banco Oracle.")
    except Exception as e:
        print(f"  ⚠  Falha ao persistir no Oracle (dados mantidos em memória): {e}")
    finally:
        conn.close()


def consultar_oracle() -> None:
    """
    Procedimento: consulta e exibe lotes diretamente do banco Oracle.
    Demonstra SELECT com cursor Oracle.
    """
    cabecalho("CONSULTA — BANCO ORACLE")

    conn = _obter_conexao_oracle()
    if conn is None:
        print("  ⚠  Banco Oracle não disponível.")
        print("  💡 Configure 'oracle_config.json' para ativar a persistência.")
        return

    sql = """
    SELECT ID_LOTE, FAZENDA, ESTADO, DATA_COLHEITA,
           TIPO_COLHEITA, PRODUCAO_TON, PERCENTUAL_PERDA,
           STATUS_PERDA, VALOR_PERDIDO_RS
    FROM   LOTES_CANA
    ORDER  BY DATA_COLHEITA DESC
    FETCH  FIRST 50 ROWS ONLY
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            linhas = cur.fetchall()

            if not linhas:
                print("  Nenhum registro no banco Oracle.")
                return

            print(f"  {'ID':<5} {'FAZENDA':<25} {'UF':<4} {'DATA':<12} "
                  f"{'TIPO':<12} {'PROD(t)':<10} {'PERDA%':<8} {'STATUS':<10} {'PREJUÍZO'}")
            linha()
            for row in linhas:
                print(f"  {row[0]:<5} {row[1]:<25} {row[2]:<4} "
                      f"{str(row[3])[:10]:<12} {row[4]:<12} "
                      f"{row[5]:<10.1f} {row[6]:<8.1f} {row[7]:<10} "
                      f"R$ {row[8]:,.2f}")
    except Exception as e:
        print(f"  ⚠  Erro na consulta Oracle: {e}")
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────
# MENU PRINCIPAL
# ──────────────────────────────────────────────────────────────────────

def menu_arquivos() -> None:
    """Submenu de manipulação de arquivos (Cap. 5)."""
    while True:
        cabecalho("GESTÃO DE ARQUIVOS")
        print("  1 - Exportar dados para JSON")
        print("  2 - Importar dados de JSON")
        print("  3 - Exportar relatório em TXT")
        print("  0 - Voltar ao menu principal")
        linha()
        opcao = input("  Opção: ").strip()

        if opcao == "1":
            salvar_json()
            pausar()
        elif opcao == "2":
            carregar_json()
            pausar()
        elif opcao == "3":
            exportar_relatorio_txt()
            pausar()
        elif opcao == "0":
            break
        else:
            print("  ⚠  Opção inválida.")
            pausar()


def menu_oracle() -> None:
    """Submenu Oracle (Cap. 6)."""
    while True:
        cabecalho("BANCO DE DADOS — ORACLE")
        print("  1 - Criar tabela LOTES_CANA (DDL)")
        print("  2 - Consultar registros no Oracle")
        print("  0 - Voltar ao menu principal")
        linha()
        opcao = input("  Opção: ").strip()

        if opcao == "1":
            criar_tabela_oracle()
            pausar()
        elif opcao == "2":
            consultar_oracle()
            pausar()
        elif opcao == "0":
            break
        else:
            print("  ⚠  Opção inválida.")
            pausar()


def menu_principal() -> None:
    """Menu principal do sistema FarmTech Fase 3."""
    while True:
        cabecalho("FARMTECH SOLUTIONS — GESTÃO DE PERDAS NA COLHEITA DE CANA")
        print("  ┌─ CADASTRO ─────────────────────────────────────────────┐")
        print("  │  1 - Registrar novo lote de colheita                   │")
        print("  │  2 - Listar todos os lotes                             │")
        print("  │  3 - Atualizar lote                                    │")
        print("  │  4 - Excluir lote                                      │")
        print("  ├─ ANÁLISE ──────────────────────────────────────────────┤")
        print("  │  5 - Relatório analítico de perdas                     │")
        print("  ├─ ARQUIVOS (JSON / TXT) ─────────────────────────────── │")
        print("  │  6 - Gestão de arquivos                                │")
        print("  ├─ BANCO DE DADOS (ORACLE) ───────────────────────────── │")
        print("  │  7 - Operações Oracle                                  │")
        print("  └────────────────────────────────────────────────────────┘")
        print("  0 - Sair")
        linha()
        opcao = input("  Opção: ").strip()

        match opcao:
            case "1": inserir_lote();         pausar()
            case "2": listar_lotes();         pausar()
            case "3": atualizar_lote();       pausar()
            case "4": excluir_lote();         pausar()
            case "5": relatorio_analitico();  pausar()
            case "6": menu_arquivos()
            case "7": menu_oracle()
            case "0":
                print("\n  Encerrando FarmTech Solutions. Até logo! 🌾\n")
                sys.exit(0)
            case _:
                print("  ⚠  Opção inválida.")
                pausar()


# ──────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  Carregando FarmTech Solutions — Fase 3...")
    carregar_json()   # Tenta carregar dados do JSON ao iniciar
    menu_principal()
