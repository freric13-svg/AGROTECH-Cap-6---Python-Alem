# ============================================================
# FarmTech Solutions — Fase 3
# Análise Estatística de Perdas na Colheita de Cana-de-Açúcar
# Script R — lê JSON gerado pelo Python e produz análises
# ============================================================

options(encoding = "UTF-8")

# Instalação condicional de dependências
pacotes <- c("jsonlite", "stats")
for (pkg in pacotes) {
  if (!require(pkg, character.only = TRUE, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
    library(pkg, character.only = TRUE)
  }
}

# ──────────────────────────────────────────────────────────
# 1. LEITURA DO JSON gerado pelo app.py Python
# ──────────────────────────────────────────────────────────

arquivo_json <- "data/lotes_cana.json"

if (!file.exists(arquivo_json)) {
  cat("╔══════════════════════════════════════════════════════╗\n")
  cat("║  ATENÇÃO: arquivo não encontrado!                    ║\n")
  cat("║  Execute o app.py e exporte os dados via menu [6].   ║\n")
  cat("║  Usando dados simulados para demonstração...         ║\n")
  cat("╚══════════════════════════════════════════════════════╝\n\n")

  # Dados simulados para demonstração (baseados em dados reais SP)
  dados <- data.frame(
    id_lote          = 1:10,
    fazenda          = c("Faz. Santa Cruz", "Faz. Boa Vista", "Faz. São João",
                         "Faz. Primavera", "Faz. Horizonte", "Faz. Verde Vale",
                         "Faz. Três Marias", "Faz. Alto Rio", "Faz. Nova Era", "Faz. Jaraguá"),
    estado           = c("SP","SP","GO","MT","MG","SP","MS","PR","SP","GO"),
    tipo_colheita    = c("Mecanizada","Manual","Mecanizada","Mecanizada","Manual",
                         "Mecanizada","Mecanizada","Manual","Mecanizada","Mecanizada"),
    area_hectares    = c(450, 80, 600, 1200, 45, 320, 850, 60, 410, 780),
    producao_bruta_t = c(45000, 7200, 62000, 130000, 4500, 31000, 88000, 5800, 42000, 80000),
    percentual_perda = c(11.2, 3.8, 13.5, 14.1, 4.2, 8.7, 12.0, 2.9, 9.5, 13.8),
    toneladas_perdidas = c(5040, 273.6, 8370, 18330, 189, 2697, 10560, 168.2, 3990, 11040),
    valor_perdido_R.  = c(604800, 32832, 1004400, 2199600, 22680, 323640, 1267200, 20184, 478800, 1324800),
    status_perda     = c("ATENÇÃO","BOM","CRÍTICO","CRÍTICO","BOM","ATENÇÃO",
                         "CRÍTICO","EXCELENTE","ATENÇÃO","CRÍTICO"),
    stringsAsFactors = FALSE
  )

} else {
  payload <- fromJSON(arquivo_json)
  df_lotes <- as.data.frame(payload$lotes)

  dados <- df_lotes[, c("id_lote", "fazenda", "estado", "tipo_colheita",
                         "area_hectares", "producao_bruta_t", "percentual_perda",
                         "toneladas_perdidas", "valor_perdido_R.", "status_perda")]
  cat("✅ Dados carregados de", arquivo_json, "\n")
  cat("   Total de lotes:", nrow(dados), "\n\n")
}

# ──────────────────────────────────────────────────────────
# 2. ANÁLISE ESTATÍSTICA DESCRITIVA
# ──────────────────────────────────────────────────────────

cat("════════════════════════════════════════════════════════\n")
cat("  FARMTECH SOLUTIONS — ANÁLISE DE PERDAS NA COLHEITA\n")
cat("════════════════════════════════════════════════════════\n\n")

cat("📊 ESTATÍSTICAS GERAIS\n")
cat("────────────────────────────────────────────────────────\n")
cat("Total de lotes analisados  :", nrow(dados), "\n")
cat("Área total colhida (ha)    :", round(sum(dados$area_hectares), 2), "\n")
cat("Produção bruta total (t)   :", format(sum(dados$producao_bruta_t), big.mark=".", scientific=FALSE), "\n")
cat("Total perdido (t)          :", format(round(sum(dados$toneladas_perdidas), 2), big.mark=".", scientific=FALSE), "\n")
cat("Prejuízo total (R$)        : R$", format(round(sum(dados$valor_perdido_R.), 2), big.mark=".", nsmall=2, scientific=FALSE), "\n\n")

cat("📈 PERCENTUAL DE PERDA (%)\n")
cat("────────────────────────────────────────────────────────\n")
perda <- dados$percentual_perda
cat("Média    :", round(mean(perda), 2), "%\n")
cat("Mediana  :", round(median(perda), 2), "%\n")
cat("Mínimo   :", round(min(perda), 2), "%\n")
cat("Máximo   :", round(max(perda), 2), "%\n")
cat("Desvio P :", round(sd(perda), 2), "%\n\n")

# ──────────────────────────────────────────────────────────
# 3. ANÁLISE POR TIPO DE COLHEITA
# ──────────────────────────────────────────────────────────

cat("🚜 ANÁLISE POR TIPO DE COLHEITA\n")
cat("────────────────────────────────────────────────────────\n")

tipos <- unique(dados$tipo_colheita)
for (tipo in tipos) {
  sub <- dados[dados$tipo_colheita == tipo, ]
  cat("\nTipo:", tipo, "\n")
  cat("  Lotes           :", nrow(sub), "\n")
  cat("  Média de perda  :", round(mean(sub$percentual_perda), 2), "%\n")
  cat("  Desvio padrão   :", round(sd(sub$percentual_perda), 2), "%\n")
  cat("  Prejuízo total  : R$", format(round(sum(sub$valor_perdido_R.), 2), big.mark=".", nsmall=2, scientific=FALSE), "\n")
}

# Referência SOCICANA
cat("\n📌 Referência SOCICANA:\n")
cat("   Manual    → perdas: 0% a 5%\n")
cat("   Mecanizada → perdas: 5% a 15%\n\n")

# ──────────────────────────────────────────────────────────
# 4. DISTRIBUIÇÃO POR STATUS
# ──────────────────────────────────────────────────────────

cat("🏷️  DISTRIBUIÇÃO POR STATUS\n")
cat("────────────────────────────────────────────────────────\n")
status_count <- table(dados$status_perda)
for (s in names(status_count)) {
  n <- status_count[s]
  pct <- round(n / nrow(dados) * 100, 1)
  barra <- paste(rep("█", n), collapse="")
  cat(sprintf("  %-12s %s (%d — %.1f%%)\n", s, barra, n, pct))
}

# ──────────────────────────────────────────────────────────
# 5. RANKING DAS FAZENDAS
# ──────────────────────────────────────────────────────────

cat("\n🏆 RANKING: MENOR PERDA → MAIOR PERDA\n")
cat("────────────────────────────────────────────────────────\n")
dados_ord <- dados[order(dados$percentual_perda), ]
for (i in seq_len(nrow(dados_ord))) {
  r <- dados_ord[i, ]
  cat(sprintf("  %2d. %-20s (%s)  %.2f%%  [%s]\n",
              i, r$fazenda, r$estado, r$percentual_perda, r$status_perda))
}

# ──────────────────────────────────────────────────────────
# 6. ESTIMATIVA DE ECONOMIA POTENCIAL
# ──────────────────────────────────────────────────────────

cat("\n💡 POTENCIAL DE ECONOMIA\n")
cat("────────────────────────────────────────────────────────\n")
cat("  Caso todas as fazendas atingissem a perda-meta de 5%:\n")

economia_total <- 0
for (i in seq_len(nrow(dados))) {
  r <- dados[i, ]
  if (r$percentual_perda > 5.0) {
    perda_atual <- r$producao_bruta_t * (r$percentual_perda / 100)
    perda_meta  <- r$producao_bruta_t * 0.05
    economia    <- (perda_atual - perda_meta) * 120   # R$/t
    economia_total <- economia_total + economia
  }
}
cat(sprintf("  Economia potencial estimada: R$ %s\n",
            format(round(economia_total, 2), big.mark=".", nsmall=2, scientific=FALSE)))

# ──────────────────────────────────────────────────────────
# 7. DADOS METEOROLÓGICOS — Open-Meteo (Ribeirão Preto/SP)
# ──────────────────────────────────────────────────────────

cat("\n════════════════════════════════════════════════════════\n")
cat("  DADOS METEOROLÓGICOS — RIBEIRÃO PRETO/SP (Polo Cana)\n")
cat("════════════════════════════════════════════════════════\n")

lat  <- -21.1767
lon  <- -47.8208
url  <- paste0(
  "https://api.open-meteo.com/v1/forecast?",
  "latitude=", lat,
  "&longitude=", lon,
  "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
  "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum",
  "&timezone=America%2FSao_Paulo",
  "&forecast_days=5"
)

tryCatch({
  resposta <- fromJSON(url)

  cat("\nCondições atuais em Ribeirão Preto:\n")
  cat("  Temperatura :", resposta$current$temperature_2m,
      resposta$current_units$temperature_2m, "\n")
  cat("  Umidade     :", resposta$current$relative_humidity_2m,
      resposta$current_units$relative_humidity_2m, "\n")
  cat("  Vento       :", resposta$current$wind_speed_10m,
      resposta$current_units$wind_speed_10m, "\n")
  cat("  Precipitação:", resposta$current$precipitation,
      resposta$current_units$precipitation, "\n")

  cat("\nPrevisão próximos 5 dias:\n")
  for (i in seq_along(resposta$daily$time)) {
    chuva <- resposta$daily$precipitation_sum[i]
    alerta <- if (!is.null(chuva) && !is.na(chuva) && chuva > 10) " ⚠ CHUVA" else ""
    cat(sprintf("  %s  Máx: %s°C  Mín: %s°C  Chuva: %smm%s\n",
                resposta$daily$time[i],
                resposta$daily$temperature_2m_max[i],
                resposta$daily$temperature_2m_min[i],
                ifelse(is.null(chuva) || is.na(chuva), "0", chuva),
                alerta))
  }
}, error = function(e) {
  cat("  ⚠  Não foi possível obter dados meteorológicos:", conditionMessage(e), "\n")
})

cat("\n════════════════════════════════════════════════════════\n")
cat("  FarmTech Solutions — Análise concluída\n")
cat("════════════════════════════════════════════════════════\n")
