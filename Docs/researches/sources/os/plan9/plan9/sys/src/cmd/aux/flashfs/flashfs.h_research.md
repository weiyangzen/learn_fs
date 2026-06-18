# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/flashfs/flashfs.h

This header defines flashfs's on-disk format constants, core structs, globals, and function interfaces.

Key behavior:
- Defines sector magic, format version, journal record type codes, record-size limits, name/file-size limits, hash-table sizes, and write sizing.
- Declares `Extent`, `Exts`, `Entry`, `Dirr`, `Jrec`, and `Renum`.
- Declares storage, conversion, journal, serving, and entry-tree APIs.
- Exposes global geometry, buffers, root entry, readonly state, generation parity, and accounting variables.

Important details:
- Maximum file size is 2 MiB and maximum filename size is 28 bytes.
- Journal record types include create variants, chmod variants, remove, write, trunc variants, summary begin/end, and summary.
- `Entry` uses a union for directory children/readers or file generation extent lists.

Filesystem relevance:
- Direct: central interface and format definition for the flashfs filesystem.
