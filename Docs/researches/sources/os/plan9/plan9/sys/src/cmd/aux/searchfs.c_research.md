# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/searchfs.c

In-memory ASCII database search filesystem. It reads a database file into memory and serves a tiny 9P filesystem with `search` and `stats` entries. Clients write query strings to `search` and read matching database records back.

Filesystem layout:
- Root directory.
- `search`: writable query endpoint and readable result stream.
- `stats`: present but currently returns empty reads.

Search query format:
- URL-style parameters `tag=val&tag1=val1`.
- Supports `search=<terms>` and `skip=<n>`.
- Multiple `?` segments use only the last search query, matching the HTTP comment in the file.

Core search behavior:
- Search terms are split on whitespace.
- Matching is ASCII case-insensitive.
- Longest term is promoted to a Boyer-Moore-like quick matcher.
- Remaining terms are checked exactly within the same newline-delimited record.
- Results are complete database lines/records.

9P behavior:
- Manual 9P server loop in `fsrun()` using `read9pmsg()`, `convM2S()`, and `convS2M()`.
- Fid table is hash-based with reference tracking.
- `Tflush` requests are ignored rather than answered directly.
- `fswrite()` replaces the fid’s active search and resets scan position.
- `fsread()` streams matches in chunks.

Dependencies and integration:
- Uses `<auth.h>` and `<fcall.h>`, but authentication is intentionally not required.
- Can mount at `/tmp` by default or publish a service file with `-s`.

Notable risks:
- Designed only for ASCII databases; case folding is custom ASCII-only.
- Entire database is loaded into memory.
- Manual 9P implementation has subtle fid/ref/open-state handling; `fswalk()` sets `f->open = 0` after `putfid()`, which is risky because `f` may have been released.
- `stats` is advertised writable/readable but returns empty content.
