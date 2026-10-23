USE RobloxAnalytics;
GO

SELECT TOP 20 
    Word,
    RawTotalOccurrences,
    TotalGamesContainingWord,
    TotalPlayerWeightedImpact,
    AvgPlayerCountPerGame
FROM vw_WeightedKeywordImpact
ORDER BY TotalPlayerWeightedImpact DESC;