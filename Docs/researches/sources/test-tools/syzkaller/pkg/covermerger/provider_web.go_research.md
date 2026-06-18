# sources/test-tools/syzkaller/pkg/covermerger/provider_web.go

Purpose: implements `FileVersProvider` by fetching file contents over HTTPS from repository web endpoints or a caller-provided proxy URI function.

Important APIs/types/functions: `FuncProxyURI`, `webGit`, `GetFileVersions`, `errFileNotFound`, `loadFile`, `isGerritServer`, and `MakeWebGit`.

Control flow: `GetFileVersions` loops over requested repo commits, calls `loadFile`, skips 404s, and returns other errors. `loadFile` builds either a proxy URI or `<repo>/plain/<file>?id=<commit>`, forces HTTPS, performs `http.Get`, reads the response, and base64-decodes the body when headers indicate Gerrit.

State and persistence: no local persistence; network reads only.

Dependencies and integration: standard `net/http`, `net/url`, base64, and `cover.GetMergeResult` for web-backed per-file rendering.

Risks: uses package-level `http.Get` with no timeout or context. It forces scheme to HTTPS, which may break non-HTTP repo strings. Gerrit detection scans all response header values for substring `gerrit`, which is heuristic. Query parameters are manually appended before URL parsing.

Test signals: no direct tests in this subset. Network/provider behavior is therefore less guarded than core merge logic.
