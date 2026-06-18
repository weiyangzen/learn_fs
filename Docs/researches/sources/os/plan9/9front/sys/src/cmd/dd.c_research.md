# File Research: sources/os/plan9/9front/sys/src/cmd/dd.c

Purpose: Plan 9 `dd` byte/block copy utility with conversions.

Key behavior:
- Parses key/value arguments like `-ibs`, `-obs`, `-bs`, `-cbs`, `-if`, `-of`, `-skip`, `-seek`, `-iseek`, `-oseek`, `-count`, `-files`, `-trunc`, `-quiet`, and `-conv`.
- Supports conversions: `ebcdic`, `ibm`, `ascii`, `block`, `unblock`, `lcase`, `ucase`, `swab`, `noerror`, and `sync`.
- `number()` parses suffix multipliers `m`, `k`, `b`, and multiplication with `x`.
- Main copy loop reads input blocks, handles count/files, noerror/sync behavior, byte swapping, fast path when ibs==obs and no conversion, and output buffering.
- `flsh()` writes pending output and counts full/partial records.
- Conversion functions handle case conversion, EBCDIC/IBM tables, fixed-length record padding/truncation, and newline conversion.
- `stats()` prints records in/out and truncated records unless quiet.

Notable details:
- Buffers are allocated with `sbrk()`.
- `dotrunc=0` opens output without truncation.
- Read errors with `noerror` seek past the failed input block and continue.
