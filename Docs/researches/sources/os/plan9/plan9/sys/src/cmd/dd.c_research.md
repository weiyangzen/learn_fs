# File Research: sources/os/plan9/plan9/sys/src/cmd/dd.c

This file implements Plan 9 `dd`, with block copying, seeking, conversion, and record statistics.

Key behaviors:
- Parses option/value pairs such as `-ibs`, `-obs`, `-bs`, `-if`, `-of`, `-skip`, `-seek`, `-iseek`, `-oseek`, `-count`, `-files`, `-trunc`, `-quiet`, and `-conv`.
- Supports conversion flags `ebcdic`, `ibm`, `ascii`, `block`, `unblock`, `lcase`, `ucase`, `swab`, `noerror`, and `sync`.
- Uses `ibs`, `obs`, and optional `bs` fast path when input/output block sizes match and no conversion is needed.
- Performs input and output seeking in block or byte units.
- Tracks full/partial input and output records plus truncated fixed-length conversion records.
- `number()` parses numeric suffixes `k`, `b`, and multiplicative `x`.
- `flsh()` writes output blocks and handles short writes/errors.
- `ascii()`, `unblock()`, `ebcdic()`, `ibm()`, and `block()` implement character-set and fixed-record transformations.
- Includes full 256-byte translation tables for EBCDIC-to-ASCII, ASCII-to-EBCDIC, and ASCII-to-IBM EBCDIC.

Notable implementation details:
- With `conv=noerror`, read errors are reported, stats are printed, and copying seeks past the failed input block.
- With `conv=sync`, short reads are padded with zeros to `ibs`.
- The program uses `sbrk()` for buffers.
- Output file truncation is controlled by the `trunc` option.
