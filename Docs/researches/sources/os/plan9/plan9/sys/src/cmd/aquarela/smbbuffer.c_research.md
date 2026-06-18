# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbbuffer.c

Core bounded read/write buffer abstraction for SMB packet parsing and construction.

Key capabilities:
- Owns or wraps packet storage with read offset, write offset, max length, and pushed read-limit state.
- Writes bytes, shorts, longs, vlongs, raw byte ranges, fixed strings, and protocol strings.
- Reads bytes, shorts, longs, vlongs, raw byte ranges, ASCII strings, UCS-2 strings, and SMB strings selected by header flags.
- Supports alignment, write/read backup, write limits, read-limit push/pop, fixups for relative/absolute offsets, filling, copying, and offset string extraction.

Interactions:
- Used by almost every SMB command, transaction, client, and response path.
- Delegates string conversion to functions declared in `smbfns.h`.

Notable details:
- `smbbuffergetucs2` optionally inserts leading `/` for paths and converts path separators/case/space according to flags.
- `smbbufferoffsetgetb` compares `offset` against `rn` but then indexes `buf[rn + offset]`; callers use it for response command byte lookup, so offset semantics deserve care.
