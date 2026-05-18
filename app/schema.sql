CREATE TABLE Users (
    User_Id INTEGER PRIMARY KEY,
    Username TEXT UNIQUE NOT NULL,
    Email UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Created_At DATETIME DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE Content (
    Content_Id INTEGER PRIMARY KEY,
    Content_Name TEXT NOT NULL,
    Created_By INTEGER NOT NULL,
    Release_Year INTEGER NOT NULL,
    Link_Url TEXT,
    Cover_Url TEXT,
    Description TEXT,
    Type TEXT NOT NULL DEFAULT 'TV Show' CHECK (Type IN (
        'TV Show',
        'Movie',
        'Youtube',
        'Anime',
        'Podcast'
    )),

    Total_Episodes INT NULL,
    Total_Seasons INT NULL,
    Is_Private BOOLEAN DEFAULT 0,
    CHECK (
        (Type = 'Youtube' AND Link_Url IS NOT NULL) OR
        (Type != 'Youtube' AND Link_Url IS NULL)
    ),
    FOREIGN KEY (Created_By) REFERENCES Users (User_Id) ON DELETE CASCADE
);

CREATE TABLE User_Content (
    User_Id INTEGER NOT NULL,
    Content_Id INTEGER NOT NULL,
    Status TEXT NOT NULL DEFAULT 'Plan to Watch'
    CHECK (
        Status IN (
            'Watching', 'Completed', 'Plan to Watch', 'Dropped', 'Paused'
        )
    ),
    Current_Episode INTEGER,
    Current_Season INTEGER NULL,
    PRIMARY KEY (User_Id, Content_Id),
    FOREIGN KEY (User_Id) REFERENCES Users (User_Id) ON DELETE CASCADE,
    FOREIGN KEY (Content_Id) REFERENCES Content (Content_Id) ON DELETE CASCADE
);

CREATE TABLE Reviews (
    User_Id INTEGER NOT NULL,
    Content_Id INTEGER NOT NULL,
    -- half stars maybe?
    Stars INTEGER NOT NULL CHECK (Stars >= 1 AND Stars <= 5),
    Body TEXT,
    Created_At DATETIME DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (User_Id, Content_Id),
    -- maybe if time we can make it so deleted users become a sentinel user
    -- like deleted_user, instead of removing the review same for public content
    FOREIGN KEY (User_Id) REFERENCES Users (User_Id) ON DELETE CASCADE,
    FOREIGN KEY (Content_Id) REFERENCES Content (Content_Id) ON DELETE CASCADE
);
