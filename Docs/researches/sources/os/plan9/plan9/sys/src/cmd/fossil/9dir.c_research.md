# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/9dir.c

Converts Fossil directory entries to 9P stat records and streams directory reads.

Key behavior:
- Allocates `DirBuf` around a `DirEntryEnum` for one-entry buffering.
- `dirDe2M()` converts Fossil `DirEntry` metadata into Plan 9 `Dir`, mapping Fossil mode bits to qid and mode flags.
- UID/GID/MUID strings are resolved through `unameByUid()`, with `(<uid>)` fallback formatting.
- `dirRead()` handles offset-zero rewind and then fills output with packed directory entries until full.

Important implementation details:
- A pending directory entry is retained if the caller's buffer is too small for `convD2M()`.
- Directory offsets are mostly ignored except for rewind.

Risks and invariants:
- `dirBufAlloc()` can fail if the directory was removed underneath the fid.
- `dirDe2M()` allocates fallback names and frees them after packing.
