# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vnops.c

## Summary
Implements AUTOFS vnode operations and node tree management.

## Main Responsibilities
- Trigger automounts from lookup, readdir, and optionally getattr/stat.
- Release vnode locks during daemon-triggered mount operations and reacquire afterward.
- Detect filesystems mounted on top of autofs nodes and delegate operations to the mounted root vnode.
- Lookup `.`/`..`, namecache entries, and autofs child nodes.
- Allow mkdir only for automountd descendants, creating synthetic directory nodes.
- Produce synthetic directory entries for `.`, `..`, and RB-tree children.
- Return synthetic directory attributes.
- Reclaim vnodes without freeing nodes; nodes are freed during explicit tree deletion.
- Manage node creation, lookup, and deletion.

## Key Interfaces
- `autofs_lookup()`, `autofs_getattr()`, `autofs_readdir()`, `autofs_mkdir()`, `autofs_trigger_vn()`.
- `autofs_node_new()`, `autofs_node_find()`, `autofs_node_delete()`.

## Risks
Triggering requires careful vnode reference and lock handling so automountd can mount over the trigger vnode. Directory offsets are based on generated dirent record lengths. Node tree mutations require `am_lock`.
