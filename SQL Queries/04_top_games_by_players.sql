USE RobloxAnalytics;
GO

SELECT TOP 20 
    Name, 
    PlayingCount, 
    Visits, 
    RatingRatio, 
    ScrapedAt
FROM Games
ORDER BY PlayingCount DESC;

