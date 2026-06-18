# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/fsif.h

Imported Xen public filesystem split-driver protocol ABI.

Purpose:
- Defines an older Xen filesystem-level split device protocol over grant-backed rings.

Key content:
- Defines request types for open, close, read, write, stat, truncate, remove, rename, create, directory list, chmod, filesystem space, and sync.
- Defines per-operation request structures, many carrying grant references for paths or data buffers.
- Defines stat response layout and directory-list result bit masks.
- Defines `struct fsif_request`, `struct fsif_response`, fixed ring entry size, derived grant counts for read/write, and `DEFINE_RING_TYPES(fsif, ...)`.
- Defines string states `init`, `ready`, `closing`, and `closed`.

Integration:
- Not used by visible 9front Xen runtime code.
- Relevant to filesystem research as a vendored Xen FS protocol, but 9front’s active virtual storage path here is `blkif.h` via `sdxen.c`.

Risks/notes:
- Variable-length grant arrays are constrained by the fixed 64-byte ring entry size.
- Protocol is less central than blkif in this tree and may be legacy/unused.
