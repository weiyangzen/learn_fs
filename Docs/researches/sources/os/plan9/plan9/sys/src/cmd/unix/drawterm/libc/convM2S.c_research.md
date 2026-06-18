# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/convM2S.c

This file decodes 9P protocol messages from bytes into `Fcall`.

Key behavior:
- `convM2S` validates the size/type/tag header, switches on 9P message type, and extracts fields for version, attach, walk, open/create, read/write, clunk/remove, stat/wstat, and replies.
- `gstring` decodes counted strings in-place and NUL-terminates them.
- `gqid` decodes qids.

Important details:
- Returns `0` on malformed sizes, unknown types, overlong name/qid counts, or truncated buffers.
- It verifies decoded byte count matches the declared 9P message size.
