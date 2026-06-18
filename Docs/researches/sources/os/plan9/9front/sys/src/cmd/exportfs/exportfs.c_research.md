# File Research: sources/os/plan9/9front/sys/src/cmd/exportfs/exportfs.c

This is the main entry point for Plan 9 `exportfs`, a 9P file server that exports a local subtree or an already-open server fd.

Key responsibilities:
- Parses options for debug, message size, root path, root shorthand, pattern file, read-only mode, and server fd file.
- Validates incompatible `-S` and `-r`/`-s` combinations.
- Loads include/exclude patterns.
- Initializes process namespace state with `rfork`.
- Determines message size from `iounit` or defaults.
- Allocates fid hash table and installs fcall formatting.
- Changes directory to the exported root when serving a local tree.
- Initializes root file structures and enters the I/O loop.

Important implementation notes:
- `-F` is accepted and ignored for backward compatibility.
- If chdir to the root fails, it sends a mount error response before exiting.
- `readonly` is global and enforced in request handlers.
