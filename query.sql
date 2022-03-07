DECLARE @dadosAtracacao TABLE(
	localidade NVARCHAR(255),
	ano INT,
	mes INT,
	numeroAtracacoes NUMERIC(36, 18),
	tempoEsperaMedio NUMERIC(36, 18),
	tempoAtracadoMedio NUMERIC(36, 18)
)

INSERT INTO @dadosAtracacao

	SELECT 
		atracacao.RegiaoGeografica AS Localidade,
		atracacao.ano AS ano,
		atracacao.mes AS mes,
		COUNT(atracacao.IDAtracacao) AS numeroAtracacoes,
		AVG(atracacao.TEsperaAtracacao) AS tempoEsperaMedio, -- TODO : tentar converter em formato de time
		AVG(atracacao.TAtracado) AS tempoAtracadoMedio
	FROM dbo.atracacao_fato AS atracacao
	WHERE
		atracacao.RegiaoGeografica = 'Nordeste'
	GROUP BY
		atracacao.ano,
		atracacao.mes,
		atracacao.RegiaoGeografica 
	
	UNION ALL 
	
	SELECT 
		atracacao.UF AS Localidade,
		atracacao.ano AS ano,
		atracacao.mes AS mes,
		COUNT(atracacao.IDAtracacao) AS numeroAtracacoes,
		AVG(atracacao.TEsperaAtracacao) AS tempoEsperaMedio, -- TODO : tentar converter em formato de time
		AVG(atracacao.TAtracado) AS tempoAtracadoMedio
	FROM dbo.atracacao_fato AS atracacao
	WHERE
		atracacao.UF = 'CE'
	GROUP BY
		atracacao.ano,
		atracacao.mes,
		atracacao.UF 

SELECT 

	tt.localidade,
	tt.ano,
	tt.mes,
	tt.numeroAtracacoes,
	tt.tempoEsperaMedio,
	tt.tempoAtracadoMedio,
	
	-- calculo da variação de atracações em relação ao ano anterior
	(
		(tt.numeroAtracacoes / tt.numeroAtracacoesAnterior - 1) * 100
	) AS variacaoAtracacaoPercentual

FROM (
	SELECT 
		t.*,
		(
			SELECT numeroAtracacoes FROM @dadosAtracacao AS da
			WHERE da.localidade = t.localidade 
				-- AND da.mes = t.mes -- todo : descoment this
				AND da.ano = (t.ano - 1)
		) AS numeroAtracacoesAnterior
	FROM @dadosAtracacao AS t
) AS tt
WHERE
	tt.ano IN (2020, 2021)
ORDER BY tt.localidade, tt.ano, tt.mes
