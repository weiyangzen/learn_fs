# sources/sync-backup/git-lfs/lfshttp/cookies.go

Purpose: Enables host-specific cookie jar loading from Git config.

Important APIs/types/functions: `isCookieJarEnabledForHost` and `getCookieJarForHost`.

Control flow: Checks `http.https://<host>.cookieFile` via URL config. If configured, expands the path and loads a cookie jar file with `cookiejarparser`.

State and persistence behavior: Reads a configured cookie file and returns an in-memory `http.CookieJar`. No writes.

Dependencies and integration points: Used by `Client.HttpClient` after transport construction. Depends on `tools.ExpandPath` and `github.com/ssgelm/cookiejarparser`.

Risks and edge cases: Only checks HTTPS host key form. Load errors are logged in `HttpClient` and do not fail client creation.

Test signals: No direct tests in this subset; behavior is only indirectly covered if `HttpClient` cookie configuration is exercised elsewhere.
