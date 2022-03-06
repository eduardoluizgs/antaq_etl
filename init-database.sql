-- *********************************
-- Database Creation
-- *********************************

IF DB_ID('ANTAQDB') IS NULL
   CREATE DATABASE ANTAQDB
GO

-- *********************************
-- Atracacao Fato Table Creation
-- *********************************

--DROP TABLE atracacao_fato
--GO

IF NOT EXISTS(
   SELECT * FROM INFORMATION_SCHEMA.TABLES
   WHERE TABLE_SCHEMA = 'dbo'
   AND  TABLE_NAME = 'atracacao_fato'
)
BEGIN
   CREATE TABLE atracacao_fato(
      IDAtracacao                      BIGINT NOT NULL PRIMARY KEY,
      CDTUP                            INT NULL,
      IDBerco                          INT NULL,
      Berco                            NVARCHAR(255) NULL,
      PortoAtracacao                   NVARCHAR(255) NULL,
      ApelidoInstalacaoPortuaria       NVARCHAR(255) NULL,
      ComplexoPortuario                NVARCHAR(255) NULL,
      TipoAutoridadePortuaria          NVARCHAR(255) NULL,
      DataAtracacao                    DATETIME NULL,
      DataChegada                      DATETIME NULL,
      DataDesatracacao                 DATETIME NULL,
      DataInicioOperacao               DATETIME NULL,
      DataTerminoOperacao              DATETIME NULL,
      Ano                              INT NULL,
      Mes                              INT NULL,
      TipoOperacao                     NVARCHAR(255) NULL,
      TipoNavegacaoAtracacao           NVARCHAR(255) NULL,
      NacionalidadeArmador             INT NULL,
      FlagMCOperacaoAtracacao          INT NULL,
      Terminal                         NVARCHAR(255) NULL,
      Municipio                        NVARCHAR(255) NULL,
      UF                               NVARCHAR(255) NULL,
      SGUF                             NVARCHAR(255) NULL,
      RegiaoGeografica                 NVARCHAR(255) NULL,
      NumeroCapitania                  NVARCHAR(255) NULL,
      NumeroIMO                        NVARCHAR(255) NULL,
      TEsperaAtracacao                 DECIMAL(15,15) NULL,
      TEsperaInicioOp                  DECIMAL(15,15) NULL,
      TOperacao                        DECIMAL(15,15) NULL,
      TEsperaDesatracacao              DECIMAL(15,15) NULL,
      TAtracado                        DECIMAL(15,15) NULL,
      TEstadia                         DECIMAL(15,15) NULL
   )
END
GO
