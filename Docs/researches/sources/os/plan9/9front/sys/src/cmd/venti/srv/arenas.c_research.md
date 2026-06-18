# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/arenas.c

Implements arena partition registration, arena map parsing/writing, and name lookup for Venti arena objects.

Key behavior:
- Maintains a fixed 512-bucket in-memory hash table from arena name to `Arena*` via `addarena`, `findarena`, and `delarena`.
- `initarenapart` reads the arena partition header from `PartBlank`, validates version/block geometry, reads the text arena map, initializes every listed arena, verifies map name matches arena header name, rejects duplicate arena names, then adds arenas to the global lookup table.
- `newarenapart` creates a blank arena partition layout, calculating table and arena bases from `PartBlank`, `HeadSize`, block size, and requested table size.
- `wbarenapart` writes both the packed arena partition header and arena map table back to disk after validating non-overlapping ranges.
- `okamap` enforces monotonically increasing, non-overlapping address ranges within bounds.
- `readarenamap` and `wbarenamap` adapt partition regions to `IFile`/`Fmt` text parsing and output.
- `parseamap` parses a count followed by tab-separated `name start stop` records, validates names and `MaxAMap`, and stores `AMapN`.
- `outputamap` emits the exact text form expected on disk.

Interactions:
- Depends on `conv.c` for packed arena partition headers.
- Depends on `ifile.c` for input abstraction.
- Used by config/index setup, formatters, checkers, and repair tools.

Notable details:
- `debugarena` is updated while initializing arenas to improve error messages.
- A failure after some arenas were added calls `freearenapart(..., 1)`, which attempts `delarena` for initialized arenas.
- `wbarenapart` has a `/* ZZZ set error message? */` comment on allocation failure.
