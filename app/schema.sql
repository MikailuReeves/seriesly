DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS user_content;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS users;
DROP FUNCTION IF EXISTS app_user_id;
DROP FUNCTION IF EXISTS validate_user_content_progress;

-- Flask sets app.current_user_id on each database connection.
-- RLS policies use this helper to compare table rows with the logged-in user.
CREATE FUNCTION app_user_id()
RETURNS INTEGER
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('app.current_user_id', true), '')::INTEGER
$$;

CREATE TABLE users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Content is the shared catalog: TV shows, movies, YouTube links, anime, etc.
-- Private content can only be read/edited by the user who created it.
CREATE TABLE content (
    content_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    content_name TEXT NOT NULL,
    created_by INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    release_year INTEGER,
    link_url TEXT,
    cover_url TEXT,
    description TEXT,
    type TEXT NOT NULL CHECK (type IN (
        'tv',
        'movie',
        'youtube',
        'anime',
        'podcast'
    )),
    total_episodes INTEGER,
    total_seasons INTEGER,
    is_private BOOLEAN NOT NULL DEFAULT false,
    -- Keep obviously invalid metadata out of the database.
    CHECK (release_year IS NULL OR release_year >= 1888),
    CHECK (total_episodes IS NULL OR total_episodes >= 0),
    CHECK (total_seasons IS NULL OR total_seasons >= 0),
    -- YouTube entries need a URL. Other content types may optionally store one.
    CHECK (
        type <> 'youtube' OR link_url IS NOT NULL
    )
);

-- RLS protects private content at the database layer, not only in Flask routes.
ALTER TABLE content ENABLE ROW LEVEL SECURITY;
ALTER TABLE content FORCE ROW LEVEL SECURITY;

-- Everyone can read public content. Private content is only visible to its owner.
CREATE POLICY content_read_policy ON content
    FOR SELECT
    USING (is_private = false OR created_by = app_user_id());

-- Users can only create content rows that belong to themselves.
CREATE POLICY content_insert_policy ON content
    FOR INSERT
    WITH CHECK (created_by = app_user_id());

-- Users may only edit/delete private content that they created.
CREATE POLICY content_update_policy ON content
    FOR UPDATE
    USING (is_private = true AND created_by = app_user_id())
    WITH CHECK (is_private = true AND created_by = app_user_id());

CREATE POLICY content_delete_policy ON content
    FOR DELETE
    USING (is_private = true AND created_by = app_user_id());

-- User-specific tracking state: status and current progress for a content item.
CREATE TABLE user_content (
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content (content_id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'watching' CHECK (
        status IN ('watching', 'paused', 'completed', 'dropped')
    ),
    current_episode INTEGER,
    current_season INTEGER,
    PRIMARY KEY (user_id, content_id),
    CHECK (current_episode IS NULL OR current_episode >= 0),
    CHECK (current_season IS NULL OR current_season >= 0)
);

-- Tracking rows are private to the user who owns them.
ALTER TABLE user_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_content FORCE ROW LEVEL SECURITY;

-- Cross-table validation cannot be expressed with a normal CHECK constraint.
-- This trigger compares user progress against the totals stored on content.
CREATE FUNCTION validate_user_content_progress()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    content_total_episodes INTEGER;
    content_total_seasons INTEGER;
BEGIN
    SELECT total_episodes, total_seasons
    INTO content_total_episodes, content_total_seasons
    FROM content
    WHERE content_id = NEW.content_id;

    IF (
        content_total_episodes IS NOT NULL
        AND NEW.current_episode IS NOT NULL
        AND NEW.current_episode > content_total_episodes
    ) THEN
        RAISE EXCEPTION 'Current episode cannot be higher than total episodes.';
    END IF;

    IF (
        content_total_seasons IS NOT NULL
        AND NEW.current_season IS NOT NULL
        AND NEW.current_season > content_total_seasons
    ) THEN
        RAISE EXCEPTION 'Current season cannot be higher than total seasons.';
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER validate_user_content_progress_trigger
BEFORE INSERT OR UPDATE ON user_content
FOR EACH ROW
EXECUTE FUNCTION validate_user_content_progress();

-- Users can only read their own tracking rows.
CREATE POLICY user_content_read_policy ON user_content
    FOR SELECT
    USING (user_id = app_user_id());

-- Users can only create tracking rows for themselves and visible content.
CREATE POLICY user_content_insert_policy ON user_content
    FOR INSERT
    WITH CHECK (
        user_id = app_user_id()
        AND EXISTS (
            SELECT 1
            FROM content
            WHERE content.content_id = user_content.content_id
        )
    );

-- Users can only update their own tracking rows and cannot move them to hidden content.
CREATE POLICY user_content_update_policy ON user_content
    FOR UPDATE
    USING (user_id = app_user_id())
    WITH CHECK (
        user_id = app_user_id()
        AND EXISTS (
            SELECT 1
            FROM content
            WHERE content.content_id = user_content.content_id
        )
    );

CREATE POLICY user_content_delete_policy ON user_content
    FOR DELETE
    USING (user_id = app_user_id());

-- Reviews are user-owned, but readable when the reviewed content is visible.
CREATE TABLE reviews (
    review_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (user_id) ON DELETE CASCADE,
    content_id INTEGER NOT NULL REFERENCES content (content_id) ON DELETE CASCADE,
    stars INTEGER NOT NULL CHECK (stars BETWEEN 1 AND 5),
    body TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, content_id)
);

-- One review per user/content is enforced above with UNIQUE.
-- RLS below controls who can read and modify review rows.
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews FORCE ROW LEVEL SECURITY;

-- Reviews are visible only if the related content is visible through content RLS.
CREATE POLICY reviews_read_policy ON reviews
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1
            FROM content
            WHERE content.content_id = reviews.content_id
        )
    );

-- Users can only create reviews as themselves, and only for visible content.
CREATE POLICY reviews_insert_policy ON reviews
    FOR INSERT
    WITH CHECK (
        user_id = app_user_id()
        AND EXISTS (
            SELECT 1
            FROM content
            WHERE content.content_id = reviews.content_id
        )
    );

-- Users can only edit their own reviews.
CREATE POLICY reviews_update_policy ON reviews
    FOR UPDATE
    USING (user_id = app_user_id())
    WITH CHECK (
        user_id = app_user_id()
        AND EXISTS (
            SELECT 1
            FROM content
            WHERE content.content_id = reviews.content_id
        )
    );

-- Users can only delete their own reviews.
CREATE POLICY reviews_delete_policy ON reviews
    FOR DELETE
    USING (user_id = app_user_id());
