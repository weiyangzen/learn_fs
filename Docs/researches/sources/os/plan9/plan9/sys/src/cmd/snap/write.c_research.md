# File Research: sources/os/plan9/plan9/sys/src/cmd/snap/write.c

Snapshot serialization writer.

Key behavior:
- Defines `pfile[]` names for process pseudo-file sections.
- Writes `Data` sections as pid/name header, fixed-width length, then raw bytes.
- Writes text and memory segments with offset, length, and page encodings.
- Emits each page as raw data (`r`), zero marker (`z`), or reference to an already written text/memory page.

Important details:
- Page references carry type, pid, and original offset.
- Validates page counts and short non-final pages with `abort()`.
- Marks pages as written as they are first emitted to enable deduplication.

Filesystem relevance:
- Direct serialization of `/proc`-derived data for later replay through `snapfs`.
