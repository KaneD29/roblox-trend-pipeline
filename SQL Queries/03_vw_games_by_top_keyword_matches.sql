USE RobloxAnalytics;
GO

CREATE OR ALTER VIEW vw_GamesByTopKeywordMatches AS
WITH TopMarketWords AS (
    SELECT TOP 50 Word
    FROM GlobalWordFrequency
    ORDER BY TotalOccurrences DESC
)
SELECT 
    g.UniverseId,
    g.Name AS GameTitle,
    g.PlayingCount,
    g.Visits,
    g.RatingRatio,
    COUNT(tm.Word) AS MatchingTopKeywordCount,
    STRING_AGG(tm.Word, ', ') AS MatchedKeywords
FROM Games g
JOIN TermMatches tm ON g.UniverseId = tm.UniverseId
JOIN TopMarketWords tmw ON tm.Word = tmw.Word
WHERE tm.CountInTitle > 0 OR tm.CountInDescription > 0 -- Checks both Title AND Description
GROUP BY 
    g.UniverseId, 
    g.Name, 
    g.PlayingCount, 
    g.Visits, 
    g.RatingRatio;
GO
USE RobloxAnalytics;
GO

SELECT TOP 20 *
FROM vw_GamesByTopKeywordMatches
ORDER BY MatchingTopKeywordCount DESC, PlayingCount DESC;