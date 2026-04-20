-- ================================================================
-- FarmTech Solutions — Fase 3
-- Scripts DDL/DML para Oracle Database (19c / 21c / 23ai)
-- Contexto: Gestão de Perdas na Colheita de Cana-de-Açúcar
-- ================================================================

-- ────────────────────────────────────────────────────────────────
-- 1. CRIAÇÃO DA TABELA PRINCIPAL
-- ────────────────────────────────────────────────────────────────
CREATE TABLE LOTES_CANA (
    ID_LOTE            NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    FAZENDA            VARCHAR2(80)   NOT NULL,
    ESTADO             CHAR(2)        NOT NULL,
    MUNICIPIO          VARCHAR2(60),
    AREA_HECTARES      NUMBER(12,4)   NOT NULL,
    DATA_COLHEITA      DATE           NOT NULL,
    TIPO_COLHEITA      VARCHAR2(15)   NOT NULL   -- 'Manual' | 'Mecanizada'
                       CHECK (TIPO_COLHEITA IN ('Manual','Mecanizada')),
    PRODUCAO_TON       NUMBER(12,2)   NOT NULL,
    PERCENTUAL_PERDA   NUMBER(5,2)    NOT NULL
                       CHECK (PERCENTUAL_PERDA BETWEEN 0 AND 100),
    TONELADAS_PERDIDAS NUMBER(12,2),
    VALOR_PERDIDO_RS   NUMBER(14,2),
    STATUS_PERDA       VARCHAR2(12)
                       CHECK (STATUS_PERDA IN ('EXCELENTE','BOM','ATENÇÃO','CRÍTICO')),
    VARIEDADE          VARCHAR2(30),
    OBSERVACAO         VARCHAR2(200),
    REGISTRO_EM        TIMESTAMP      DEFAULT SYSTIMESTAMP NOT NULL,
    ATUALIZADO_EM      TIMESTAMP
);

-- Comentários na tabela (documentação no banco)
COMMENT ON TABLE  LOTES_CANA IS 'Registro de lotes de colheita de cana-de-açúcar — FarmTech Solutions Fase 3';
COMMENT ON COLUMN LOTES_CANA.PERCENTUAL_PERDA IS 'Perda aferida no campo. Ref: Manual 0-5%, Mecanizada 5-15% (SOCICANA)';
COMMENT ON COLUMN LOTES_CANA.STATUS_PERDA     IS 'EXCELENTE=abaixo do mínimo da faixa; BOM=até 50% da faixa; ATENÇÃO=dentro da faixa; CRÍTICO=acima da faixa';

-- ────────────────────────────────────────────────────────────────
-- 2. ÍNDICES PARA CONSULTAS FREQUENTES
-- ────────────────────────────────────────────────────────────────
CREATE INDEX IDX_LOTES_ESTADO    ON LOTES_CANA (ESTADO);
CREATE INDEX IDX_LOTES_DATA      ON LOTES_CANA (DATA_COLHEITA);
CREATE INDEX IDX_LOTES_STATUS    ON LOTES_CANA (STATUS_PERDA);
CREATE INDEX IDX_LOTES_COLHEITA  ON LOTES_CANA (TIPO_COLHEITA);

-- ────────────────────────────────────────────────────────────────
-- 3. DADOS DE EXEMPLO (para testes sem o app Python)
-- ────────────────────────────────────────────────────────────────
INSERT INTO LOTES_CANA (FAZENDA, ESTADO, MUNICIPIO, AREA_HECTARES, DATA_COLHEITA,
                         TIPO_COLHEITA, PRODUCAO_TON, PERCENTUAL_PERDA,
                         TONELADAS_PERDIDAS, VALOR_PERDIDO_RS, STATUS_PERDA,
                         VARIEDADE, OBSERVACAO)
VALUES ('Fazenda Santa Cruz', 'SP', 'Ribeirão Preto', 450,
        TO_DATE('2025-06-15','YYYY-MM-DD'), 'Mecanizada', 45000,
        11.2, 5040, 604800, 'ATENÇÃO', 'RB867515', 'Solo argiloso — colhedora regulada');

INSERT INTO LOTES_CANA (FAZENDA, ESTADO, MUNICIPIO, AREA_HECTARES, DATA_COLHEITA,
                         TIPO_COLHEITA, PRODUCAO_TON, PERCENTUAL_PERDA,
                         TONELADAS_PERDIDAS, VALOR_PERDIDO_RS, STATUS_PERDA,
                         VARIEDADE, OBSERVACAO)
VALUES ('Fazenda Boa Vista', 'SP', 'Piracicaba', 80,
        TO_DATE('2025-07-20','YYYY-MM-DD'), 'Manual', 7200,
        3.8, 273.6, 32832, 'BOM', 'SP81-3250', 'Equipe treinada, baixa perda');

INSERT INTO LOTES_CANA (FAZENDA, ESTADO, MUNICIPIO, AREA_HECTARES, DATA_COLHEITA,
                         TIPO_COLHEITA, PRODUCAO_TON, PERCENTUAL_PERDA,
                         TONELADAS_PERDIDAS, VALOR_PERDIDO_RS, STATUS_PERDA,
                         VARIEDADE, OBSERVACAO)
VALUES ('Fazenda Horizonte', 'GO', 'Rio Verde', 600,
        TO_DATE('2025-08-05','YYYY-MM-DD'), 'Mecanizada', 62000,
        13.5, 8370, 1004400, 'CRÍTICO', 'CTC4', 'Revisão da colhedora necessária');

INSERT INTO LOTES_CANA (FAZENDA, ESTADO, MUNICIPIO, AREA_HECTARES, DATA_COLHEITA,
                         TIPO_COLHEITA, PRODUCAO_TON, PERCENTUAL_PERDA,
                         TONELADAS_PERDIDAS, VALOR_PERDIDO_RS, STATUS_PERDA,
                         VARIEDADE, OBSERVACAO)
VALUES ('Fazenda Primavera', 'MG', 'Uberaba', 45,
        TO_DATE('2025-09-10','YYYY-MM-DD'), 'Manual', 4500,
        2.9, 130.5, 15660, 'EXCELENTE', 'RB92579', 'Melhor lote da safra');

COMMIT;

-- ────────────────────────────────────────────────────────────────
-- 4. QUERIES ANALÍTICAS
-- ────────────────────────────────────────────────────────────────

-- 4.1 Resumo geral da safra
SELECT
    COUNT(*)                           AS TOTAL_LOTES,
    ROUND(SUM(AREA_HECTARES), 2)       AS AREA_TOTAL_HA,
    ROUND(SUM(PRODUCAO_TON), 2)        AS PRODUCAO_TOTAL_T,
    ROUND(SUM(TONELADAS_PERDIDAS), 2)  AS PERDAS_TOTAL_T,
    ROUND(SUM(VALOR_PERDIDO_RS), 2)    AS PREJUIZO_TOTAL_RS,
    ROUND(AVG(PERCENTUAL_PERDA), 2)    AS MEDIA_PERDA_PCT
FROM LOTES_CANA;

-- 4.2 Análise por tipo de colheita
SELECT
    TIPO_COLHEITA,
    COUNT(*)                          AS LOTES,
    ROUND(AVG(PERCENTUAL_PERDA), 2)   AS MEDIA_PERDA,
    ROUND(MIN(PERCENTUAL_PERDA), 2)   AS MIN_PERDA,
    ROUND(MAX(PERCENTUAL_PERDA), 2)   AS MAX_PERDA,
    ROUND(STDDEV(PERCENTUAL_PERDA),2) AS DESVIO_PERDA,
    ROUND(SUM(VALOR_PERDIDO_RS), 2)   AS PREJUIZO_RS
FROM LOTES_CANA
GROUP BY TIPO_COLHEITA
ORDER BY MEDIA_PERDA;

-- 4.3 Análise por estado
SELECT
    ESTADO,
    COUNT(*)                         AS LOTES,
    ROUND(AVG(PERCENTUAL_PERDA), 2)  AS MEDIA_PERDA_PCT,
    ROUND(SUM(PRODUCAO_TON), 2)      AS PRODUCAO_TOTAL_T,
    ROUND(SUM(VALOR_PERDIDO_RS), 2)  AS PREJUIZO_RS
FROM LOTES_CANA
GROUP BY ESTADO
ORDER BY MEDIA_PERDA_PCT;

-- 4.4 Ranking de desempenho (melhores fazendas)
SELECT
    ID_LOTE,
    FAZENDA,
    ESTADO,
    TIPO_COLHEITA,
    PERCENTUAL_PERDA,
    STATUS_PERDA,
    TO_CHAR(DATA_COLHEITA, 'DD/MM/YYYY') AS DATA_COLHEITA_FMT,
    VALOR_PERDIDO_RS
FROM LOTES_CANA
ORDER BY PERCENTUAL_PERDA ASC;

-- 4.5 Distribuição por status de perda
SELECT
    STATUS_PERDA,
    COUNT(*)                                 AS QTD,
    ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 1) AS PCT
FROM LOTES_CANA
GROUP BY STATUS_PERDA
ORDER BY
    CASE STATUS_PERDA
        WHEN 'EXCELENTE' THEN 1
        WHEN 'BOM'       THEN 2
        WHEN 'ATENÇÃO'   THEN 3
        WHEN 'CRÍTICO'   THEN 4
    END;

-- 4.6 Lotes críticos — ação imediata necessária
SELECT
    FAZENDA,
    ESTADO,
    PERCENTUAL_PERDA,
    TONELADAS_PERDIDAS,
    VALOR_PERDIDO_RS,
    TO_CHAR(DATA_COLHEITA, 'DD/MM/YYYY') AS DATA,
    OBSERVACAO
FROM LOTES_CANA
WHERE STATUS_PERDA = 'CRÍTICO'
ORDER BY PERCENTUAL_PERDA DESC;
