USE RobloxAnalytics;
GO

CREATE OR ALTER VIEW vw_WeightedKeywordImpact AS
SELECT 
    tm.Word,
    -- Basic counts
    SUM(tm.CountInTitle + tm.CountInDescription) AS RawTotalOccurrences,
    COUNT(DISTINCT g.UniverseId) AS TotalGamesContainingWord,
    
    -- Player-Weighted Impact Scores
    SUM((tm.CountInTitle + tm.CountInDescription) * g.PlayingCount) AS TotalPlayerWeightedImpact,
    
    -- Average player count per game that features this term
    AVG(g.PlayingCount) AS AvgPlayerCountPerGame,
    
    -- Log-weighted score to balance out ultra-viral games
    ROUND(SUM((tm.CountInTitle + tm.CountInDescription) * LOG10(g.PlayingCount + 1)), 2) AS LogWeightedImpact
FROM TermMatches tm
JOIN Games g ON tm.UniverseId = g.UniverseId
GROUP BY tm.Word;
GO 

USE RobloxAnalytics;
GO

CREATE OR ALTER VIEW vw_WeightedKeywordImpact AS
SELECT 
    tm.Word,
    -- Basic counts
    SUM(tm.CountInTitle + tm.CountInDescription) AS RawTotalOccurrences,
    COUNT(DISTINCT g.UniverseId) AS TotalGamesContainingWord,
    
    -- Player-Weighted Impact Scores
    SUM((tm.CountInTitle + tm.CountInDescription) * g.PlayingCount) AS TotalPlayerWeightedImpact,
    
    -- Average player count per game that features this term
    AVG(g.PlayingCount) AS AvgPlayerCountPerGame,
    
    -- Log-weighted score to balance out ultra-viral games
    ROUND(SUM((tm.CountInTitle + tm.CountInDescription) * LOG10(g.PlayingCount + 1)), 2) AS LogWeightedImpact
FROM TermMatches tm
JOIN Games g ON tm.UniverseId = g.UniverseId
GROUP BY tm.Word;
GO

