# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/string.c

Permanent interned-string table for 9nfs.

Key responsibilities:
- Stores unique strings in a 509-bucket hash table.
- Provides `strfind` for lookup without insertion and `strstore` for lookup-or-insert.
- Moves found entries to the front of their bucket for locality.
- Provides `strprint` to dump bucket indices and stored strings.
- Allocates permanent `Strnode` storage from large bump-allocated chunks.

Dependencies:
- Requires `Strnode` from `all.h`.
- Uses `panic`, `malloc`, `memmove`, `strcmp`, and `strlen`.

Notable risks:
- Strings are never freed by design.
- Hash bucket movement is not locked; callers must avoid concurrent mutation or provide external serialization.
