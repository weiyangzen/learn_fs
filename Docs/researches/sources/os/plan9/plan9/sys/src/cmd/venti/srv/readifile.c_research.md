# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/readifile.c

Purpose: Small utility to read an index file and write its raw block data to stdout.

Key behavior:
- Expects exactly one filename.
- Calls `readifile`, then writes `ifile.b->data` with length `ifile.b->len`.

Dependencies:
- Uses `IFile` and Venti index-file reader helpers.

Notable details:
- Minimal wrapper with no extra interpretation of the index file contents.
