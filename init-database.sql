-- *********************************
-- Database Creation
-- *********************************

IF DB_ID('ANTAQDB') IS NULL
   CREATE DATABASE ANTAQDB
GO

-- *********************************
-- Atracacao Fato Table Creation
-- *********************************

/*
DROP TABLE atracacao_fato
GO
*/

IF NOT EXISTS(
   SELECT * FROM INFORMATION_SCHEMA.TABLES
   WHERE TABLE_SCHEMA = 'dbo'
   AND  TABLE_NAME = 'atracacao_fato'
)
BEGIN
   CREATE TABLE atracacao_fato(
      IDAtracacao                       BIGINT           NOT NULL    PRIMARY KEY,
      CDTUP                             INT              NULL,
      IDBerco                           INT              NULL,
      Berco                             NVARCHAR(255)    NULL,
      PortoAtracacao                    NVARCHAR(255)    NULL,
      ApelidoInstalacaoPortuaria        NVARCHAR(255)    NULL,
      ComplexoPortuario                 NVARCHAR(255)    NULL,
      TipoAutoridadePortuaria           NVARCHAR(255)    NULL,
      DataAtracacao                     DATETIME         NULL,
      DataChegada                       DATETIME         NULL,
      DataDesatracacao                  DATETIME         NULL,
      DataInicioOperacao                DATETIME         NULL,
      DataTerminoOperacao               DATETIME         NULL,
      Ano                               INT              NULL,
      Mes                               INT              NULL,
      TipoOperacao                      NVARCHAR(255)    NULL,
      TipoNavegacaoAtracacao            NVARCHAR(255)    NULL,
      NacionalidadeArmador              INT              NULL,
      FlagMCOperacaoAtracacao           INT              NULL,
      Terminal                          NVARCHAR(255)    NULL,
      Municipio                         NVARCHAR(255)    NULL,
      UF                                NVARCHAR(255)    NULL,
      SGUF                              NVARCHAR(255)    NULL,
      RegiaoGeografica                  NVARCHAR(255)    NULL,
      NumeroCapitania                   NVARCHAR(255)    NULL,
      NumeroIMO                         NVARCHAR(255)    NULL,
      TEsperaAtracacao                  NUMERIC(36, 18)  NULL,
      TEsperaInicioOp                   NUMERIC(36, 18)  NULL,
      TOperacao                         NUMERIC(36, 18)  NULL,
      TEsperaDesatracacao               NUMERIC(36, 18)  NULL,
      TAtracado                         NUMERIC(36, 18)  NULL,
      TEstadia                          NUMERIC(36, 18)  NULL
   )
END
GO

-- *********************************
-- Carga Fato Table Creation
-- *********************************

/*
DROP TABLE carga_fato
GO
*/

IF NOT EXISTS(
   SELECT * FROM INFORMATION_SCHEMA.TABLES
   WHERE TABLE_SCHEMA = 'dbo'
   AND  TABLE_NAME = 'carga_fato'
)
BEGIN
   CREATE TABLE carga_fato(
      IDCarga                           BIGINT           NOT NULL PRIMARY KEY,
      IDAtracacao                       BIGINT           NULL,
      Origem                            NVARCHAR(255)    NULL,
      Destino                           NVARCHAR(255)    NULL,
      CDMercadoria                      INT              NULL,
      TipoOperacaoCarga                 NVARCHAR(255)    NULL,
      CargaGeralAcondicionamento        NVARCHAR(255)    NULL,
      ConteinerEstado                   NVARCHAR(255)    NULL,
      TipoNavegacao                     NVARCHAR(255)    NULL,
      FlagAutorizacao                   BIT              NULL,
      FlagCabotagem                     BIT              NULL,
      FlagCabotagemMovimentacao         BIT              NULL,
      FlagConteinerTamanho              BIT              NULL,
      FlagLongoCurso                    BIT              NULL,
      FlagMCOperacaoCarga               BIT              NULL,
      FlagOffshore                      BIT              NULL,
      FlagTransporteViaInterioir        BIT              NULL,
      PercursoTransporteViasInteriores  NVARCHAR(255)    NULL,
      PercursoTransporteInteriores      NVARCHAR(255)    NULL,
      STNaturezaCarga                   NVARCHAR(255)    NULL,
      STSH2                             NVARCHAR(255)    NULL,
      STSH4                             NVARCHAR(255)    NULL,
      NaturezaCarga                     NVARCHAR(255)    NULL,
      Sentido                           NVARCHAR(255)    NULL,
      TEU                               INT              NULL,
      QTCarga                           INT              NULL,
      VLPesoCargaBruta                  NUMERIC(15, 2)   NULL,
   )

   ALTER TABLE dbo.carga_fato
   ADD FOREIGN KEY (IDAtracacao) REFERENCES dbo.atracacao_fato(IDAtracacao)
END
GO

/*
SELECT * FROM DBO.atracacao_fato
SELECT * FROM DBO.carga_fato
*/
