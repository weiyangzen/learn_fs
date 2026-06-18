# Research: sources/object-store/minio-mc/cmd/ls.go

Purpose: contains listing output models, version grouping, sorting, summary, and core listing loop for `mc ls`.

Important APIs/types/functions: `contentMessage`, `getOSDependantKey`, `getKey`, `generateContentMessages`, `sortObjectVersions`, `summaryMessage`, `printObjectVersions`, `doListOptions`, and `doList`.

Control flow: `doList` iterates `clnt.List` with recursive, incomplete, rewind, versions, delete markers, and zip options. It filters by storage class, groups consecutive entries by path, prints one or all versions, accumulates summary totals, and returns an exit status if listing errors occurred. `generateContentMessages` normalizes keys relative to the listed prefix, strips ETag quotes, marks folders/files, and sets version ordinals.

State and persistence: read-only listing; only console/JSON output.

Dependencies/integration points: client abstraction, `ClientContent`, `ListOptions`, `printMsg`, humanize, colorjson, console colors from `ls-main.go`.

Risks: version grouping assumes list output is ordered by path. Summary totals count versions/delete markers according to list output, not necessarily unique logical objects. `getOSDependantKey` currently uses `/` regardless of OS despite its name.

Test signals: `ls_test.go` is effectively empty. Tests should cover version sorting, prefix trimming, storage-class filtering, summary counts, and error continuation.
