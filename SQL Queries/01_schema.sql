CREATE DATABASE RobloxAnalytics;
GO

USE RobloxAnalytics;
GO

CREATE TABLE Games (
    UniverseId BIGINT PRIMARY KEY,
    PlaceId BIGINT,
    Name NVARCHAR(255),
    Description NVARCHAR(MAX),
    PlayingCount INT,
    Visits BIGINT,
    FavoritedCount INT,
    UpVotes INT,
    DownVotes INT,
    RatingRatio FLOAT,
    ScrapedAt DATETIME DEFAULT GETDATE()
);

CREATE TABLE TermMatches (
    MatchID INT IDENTITY(1,1) PRIMARY KEY,
    UniverseId BIGINT FOREIGN KEY REFERENCES Games(UniverseId),
    Keyword NVARCHAR(100),
    FoundInTitle BIT,
    FoundInDescription BIT
);