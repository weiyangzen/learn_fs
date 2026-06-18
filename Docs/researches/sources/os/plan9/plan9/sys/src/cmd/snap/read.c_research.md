# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/read.c

Reader for serialized process snapshot files.

Key behavior:
- Validates the `process snapshot` header.
- Reads per-process sections into `Proc` records.
- Decodes `/proc` metadata sections, text segments, and memory segment lists.
- Reconstructs pages from raw data, zero markers, or references to previously read text/memory pages.
- Provides `findpage()` for locating a page by pid, type, and offset.

Important details:
- Snapshot numeric fields are fixed-width decimal strings.
- Page references can point to previous process text or memory pages.
- Bad references and malformed segment records call `panic()`.

Filesystem relevance:
- Indirect: reconstructs process filesystem snapshots previously captured from `/proc`.
