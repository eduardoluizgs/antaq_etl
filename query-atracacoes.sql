-- *****************************************************************
--
-- Query com resumo das atracacoes por ano e localidade
--
-- *****************************************************************

-- *****************************************************************
-- cria tabela temporaria para armazenar os dados já agrupados
-- *****************************************************************

DECLARE @dadosAtracacaoTable TABLE(
    localidade NVARCHAR(255),
    ano INT,
    mes INT,
    numeroAtracacoes NUMERIC(36, 18),
    tempoEsperaMedio NUMERIC(36, 18),
    tempoAtracadoMedio NUMERIC(36, 18)
)

-- *****************************************************************
-- insere os dados na tabela temporaria
-- *****************************************************************

INSERT INTO @dadosAtracacaoTable

    -- seleciona os dados referente ao estado CE
    SELECT
        atracacao.SGUF                          AS Localidade,
        atracacao.ano                           AS ano,
        atracacao.mes                           AS mes,
        COUNT(atracacao.IDAtracacao)            AS numeroAtracacoes,
        AVG(atracacao.TEsperaAtracacao)         AS tempoEsperaMedio,
        AVG(atracacao.TAtracado)                AS tempoAtracadoMedio
    FROM dbo.atracacao_fato AS atracacao
    WHERE
        atracacao.SGUF = 'CE'
    GROUP BY
        atracacao.SGUF,
        atracacao.ano,
        atracacao.mes

    UNION ALL

    -- seleciona os dados referente a região NORDESTE
    SELECT
        atracacao.RegiaoGeografica              AS Localidade,
        atracacao.ano                           AS ano,
        atracacao.mes                           AS mes,
        COUNT(atracacao.IDAtracacao)            AS numeroAtracacoes,
        AVG(atracacao.TEsperaAtracacao)         AS tempoEsperaMedio,
        AVG(atracacao.TAtracado)                AS tempoAtracadoMedio
    FROM dbo.atracacao_fato AS atracacao
    WHERE
        atracacao.RegiaoGeografica = 'Nordeste'
    GROUP BY
        atracacao.RegiaoGeografica,
        atracacao.ano,
        atracacao.mes

    UNION ALL

    -- seleciona os dados referente ao brasil
    SELECT
        'Brasil'                                AS Localidade,
        atracacao.ano                           AS ano,
        atracacao.mes                           AS mes,
        COUNT(atracacao.IDAtracacao)            AS numeroAtracacoes,
        AVG(atracacao.TEsperaAtracacao)         AS tempoEsperaMedio,
        AVG(atracacao.TAtracado)                AS tempoAtracadoMedio
    FROM dbo.atracacao_fato AS atracacao
    WHERE atracacao.SGUF IN (
        'RO', 'AC', 'AM', 'RR', 'PA', 'AP', 'TO', 'MA', 'PI',
        'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA', 'MG', 'ES',
        'RJ', 'SP', 'PR', 'SC', 'RS', 'MS', 'MT', 'GO', 'DF'
    )
    GROUP BY
        atracacao.ano,
        atracacao.mes

-- *****************************************************************
-- seleciona os dados finais que serão retornados para o usuário
-- *****************************************************************

SELECT

    tt.localidade,
    tt.ano,
    tt.mes,
    tt.numeroAtracacoes,

    -- ajusta o campo tempoEsperaMedio para o formato de hora
    CAST(CONVERT(VARCHAR,
        DATEADD(SECOND, tt.tempoEsperaMedio * 3600, 0),108) AS TIME
    ) AS tempoEsperaMedio,

    -- ajusta o campo tempoAtracadoMedio para o formato de hora
    CAST(CONVERT(VARCHAR,
        DATEADD(SECOND, tt.tempoAtracadoMedio * 3600, 0),108) AS TIME
    ) AS tempoAtracadoMedio,

    -- calcula a variação de atracações em relação ao ano anterior
    (
        CASE
            WHEN tt.numeroAtracacoes > 0 AND tt.numeroAtracacoesAnterior > 0 THEN
                ((tt.numeroAtracacoes / tt.numeroAtracacoesAnterior) - 1) * 100
            ELSE tt.numeroAtracacoesAnterior
        END
    ) AS variacaoAtracacaoPercentual

FROM (

    SELECT
        t.*,
        -- captura numero de atracacoes do ano anterior
        (
            SELECT numeroAtracacoes FROM @dadosAtracacaoTable AS da
            WHERE da.localidade = t.localidade
                AND da.mes = t.mes
                AND da.ano = (t.ano - 1)
        ) AS numeroAtracacoesAnterior
    FROM @dadosAtracacaoTable AS t

) AS tt
WHERE tt.ano IN (2020, 2021)            -- somente para os anos especificados
ORDER BY tt.localidade, tt.ano, tt.mes
