# File Research: sources/os/plan9/plan9/sys/src/lib9p/ramfs.c

This file is a simple lib9p-backed in-memory file server example/application.

Key behavior:
- Defines `Ramfile` with a data buffer and byte length.
- `fsread` reads from a file’s in-memory buffer respecting offset/count.
- `fswrite` reallocates storage as needed, writes request data, updates file length, and reports bytes written.
- `fscreate` creates a tree-backed file with `createfile`, attaches a new `Ramfile`, updates fid state, and returns the qid.
- `fsopen` handles `OTRUNC` by clearing in-memory length and visible file length.
- `fsdestroyfile` frees per-file data.
- `main` creates an alloctree root, parses `-D`, `-a`, `-s`, and `-m`, then serves by network listen and/or postmount.

Important dependencies:
- Uses the in-memory tree from `file.c`.
- Uses listen/postmount wrappers from `listen.c`, `post.c`, `rfork.c`, or `thread.c`.

Notable details:
- The server requires at least one of address, service name, or mount point.
- Permission enforcement is mostly delegated to generic `srv.c` handling and tree metadata.
