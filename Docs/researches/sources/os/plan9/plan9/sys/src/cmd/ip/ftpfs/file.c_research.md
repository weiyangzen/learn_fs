# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ftpfs/file.c

`file.c` implements local caching for `ftpfs` remote files.

Key behavior:
- Maintains up to 128 cached `File` entries.
- `fileget` returns an existing cache for a node or allocates/reuses a clean least-recently-used slot.
- `filefree` closes/removes temp files, frees memory, and detaches cache from the node.
- First 1024 bytes are cached in memory; later content spills to a temp file.
- `fileread` reads from memory or temp file based on offset.
- `filewrite` writes into memory/temp storage, grows cached length, and updates node length.
- `filedirty`, `fileclean`, and `fileisdirty` track writeback state.
- `uncachedir` frees clean temp-backed child caches to limit temp file count.

Important dependencies:
- Uses `Node` from `ftpfs.h` and `uncache`/`seterr`.

Notable risks/quirks:
- Temp files are created with `mktemp` and ORCLOSE.
- Only clean files can be evicted automatically.
