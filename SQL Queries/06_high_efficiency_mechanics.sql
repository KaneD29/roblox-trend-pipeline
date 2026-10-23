USE RobloxAnalytics;
GO

SELECT TOP 20 
    Word,
    TotalGamesContainingWord,
    AvgPlayerCountPerGame,
    TotalPlayerWeightedImpact
FROM vw_WeightedKeywordImpact
WHERE TotalGamesContainingWord >= 3 -- Filter out one-off titles
ORDER BY AvgPlayerCountPerGame DESC;