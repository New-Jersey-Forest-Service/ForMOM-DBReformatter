--
-- Extract Tables with Inventory years from INVYEARS
--

-- STANDINIT
CREATE TABLE FVS_STANDINIT_PLOT_INVYEARST AS 
	SELECT * FROM FVS_STANDINIT_PLOT
	WHERE INV_YEAR IN (2015, 2016, 2017, 2018, 2019, 2020)
;

-- PLOTINIT
CREATE TABLE FVS_PLOTINIT_PLOT_INVYEARST AS 
	SELECT * FROM FVS_PLOTINIT_PLOT
	WHERE INV_YEAR IN (2015, 2016, 2017, 2018, 2019, 2020)
;

-- TREEINIT
-- Treeinit doesn't have an INV_YEAR column so we cross reference with
-- other tables and join with STAND_CN
CREATE TABLE FVS_TREEINIT_PLOT_INVYEARST AS
	SELECT FVS_TREEINIT_PLOT.*
	FROM FVS_TREEINIT_PLOT, FVS_STANDINIT_PLOT_INVYEARST
	WHERE FVS_TREEINIT_PLOT.STAND_CN = FVS_STANDINIT_PLOT_INVYEARST.STAND_CN
;


