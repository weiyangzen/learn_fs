# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/unixnames.c

Unix uid/gid and hostname mapping support for 9nfs authentication.

Key responsibilities:
- Maps `(server, client IP)` pairs to `Unixidmap` entries using regexes and DNS-domain lookup.
- Reads mapping config files and refreshes user/group maps when backing files change.
- Supports config lines that execute helper commands prefixed with `!`.
- Parses Unix-style passwd/group-like files and Plan 9-style id files.
- Provides `name2id()`, `id2name()`, and `idprint()` lookup/debug helpers.
- Reuses freed `Unixid` nodes through a local free list.

Important behavior:
- Uses client IP rather than hostname because some clients omit host identity.
- Server and client patterns are compiled regexes and must match the entire string.
- Stale mappings are invalidated when config entries disappear.
- `checkunixmap()` reloads when file mtime is newer than the stored timestamp.

Dependencies:
- Uses `strparse()`, `system()`, regex APIs, DNS helper `getdom()`, `strstore()`, and Plan 9 `bio`.

Notable risks:
- Helper command execution from config is powerful and depends on trusted config files.
- Domain lookup/cache behavior affects auth mapping correctness.
- `pair2idmap()` returns `r` after the scan; if no regex matches, `r` is nil by loop termination but this is implicit.
