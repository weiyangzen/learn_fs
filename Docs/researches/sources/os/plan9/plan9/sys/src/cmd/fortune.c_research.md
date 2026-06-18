# File Research: sources/os/plan9/plan9/sys/src/cmd/fortune.c

Random fortune-line picker with optional persistent index.

Key behavior:
- Opens a supplied fortune file or `/sys/games/lib/fortunes`.
- If using the default file, uses `/sys/games/lib/fortunes.index` when current, or creates/updates it.
- Old index path selects a random 4-byte offset and reads that line.
- No-index path uses reservoir sampling while optionally writing offsets to a new index.
- Prints the selected line or a misfortune message on failure.

Important implementation details:
- Index offsets are stored little-endian in four bytes.
- If an existing index has length zero, it is treated as being rewritten by another process and ignored.

Risks and invariants:
- `choice` is a fixed 2048-byte buffer and long fortune lines may overflow through `strcpy()`.
- Index format is limited to 32-bit offsets.
