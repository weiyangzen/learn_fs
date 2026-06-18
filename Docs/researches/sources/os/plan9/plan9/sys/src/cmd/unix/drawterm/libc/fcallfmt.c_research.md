# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fcallfmt.c

This file formats 9P `Fcall`, `Qid`, `Dir`, and payload data for diagnostics.

Key behavior:
- `fcallfmt` renders each 9P message type with its relevant fields.
- `dirfmt` and `fdirconv` format `Dir` values.
- `qidtype` formats qid type bits.
- `dumpsome` prints bounded data payload previews.

Important details:
- Useful for tracing filesystem protocol traffic.
- Limits payload dumps to avoid huge diagnostic strings.
