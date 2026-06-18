# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/conv.c

Role: Encoder, decoder, and formatter for flashfs journal records (`Jrec`).

Encoding:
- `convJ2M` converts in-memory journal records to compact byte records, using variable-length 3-byte integers via `putc3`.
- Generic create/chmod/truncate types are rewritten into compact variants based on directory and high mode bits.
- Write sizes are stored as `size - 1`.

Decoding:
- `convM2J` reverses compact record variants into generic `FT_create`, `FT_chmod`, `FT_trunc`, `FT_WRITE`, etc.
- It copies names with `MAXNSIZE+1` limit and rejects names longer than `MAXNSIZE`.

Formatting:
- `Jconv` prints human-readable journal records for diagnostics and debug logging via `%J`.

Record families:
- Create, chmod, remove, write, append-write, truncate, summary begin, summary marker, and summary end.
