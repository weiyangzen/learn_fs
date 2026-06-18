# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/ms2.c

This file converts executable or binary data to Motorola S-record output.

Key behavior:
- Reads Plan 9 executable headers through `mach.h` unless binary mode is selected.
- Emits text and data segments, or only data segment with `-d`.
- Supports S1, S2, and S3 record widths.
- Can output raw binary file contents as S-records.
- Optionally halfword-swaps data before emitting.

Important details:
- Default record payload size is 32 bytes.
- `-a` selects start address and `-p` page-aligns data after text.
- Emits S9/S7 termination records unless suppressed.

Filesystem relevance:
- Indirect binary conversion utility.
