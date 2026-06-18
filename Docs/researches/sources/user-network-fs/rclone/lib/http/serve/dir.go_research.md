# sources/user-network-fs/rclone/lib/http/serve/dir.go

Source read signal: reviewed complete local file (254 lines, sha256 0049e810d80f6ab8).

Purpose: Represents and renders HTTP directory listings for rclone serve modes.

Important APIs/types/functions: Types `DirEntry`, `Directory`, and `Crumb`; functions/methods `NewDirectory`, `SetQuery`, `AddHTMLEntry`, `AddEntry`, `Error`, `ProcessQueryParams`, sorter types, and `Serve`.

Control flow: `NewDirectory` builds title/name/zip URL and breadcrumbs. Add methods append escaped entry URLs and optional zip links. `ProcessQueryParams` chooses and applies name, dir-first, size, or time sort with optional descending order. `Serve` accounts the directory transfer, executes the HTML template into a buffer, sets content headers, and writes it.

State and persistence behavior: `Directory` holds in-memory listing state only. `Error` records counted/logged errors and may write an HTTP 500 response.

Dependencies and integration points: Uses rclone `fs`, `accounting`, `rest.URLPathEscape`, `html/template`, and `net/http`. Called by HTTP/WebDAV serving code when presenting directories.

Risks and test signals: URL escaping for colon/quotes and query handling are important. Sorting directory sizes uses a sentinel offset to keep directories predictable. Template execution errors become counted transfer errors.
