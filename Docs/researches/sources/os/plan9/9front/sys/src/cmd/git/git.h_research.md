# File Research: sources/os/plan9/9front/sys/src/cmd/git/git.h

Shared 9front git declarations, object model, protocol model, and utility prototypes.

Key contents:
- Defines git object type constants, object cache flags, connection types, sizes, and endian helpers.
- Defines `Hash`, `Object`, commit/tree info, pack/index/object-list state, object sets, priority queues, delta tables, and delta ops.
- Declares object I/O, ref resolution, pack writing/indexing, object-set, object-list, utility, delta, protocol, and queue APIs.
- Declares custom formatters for hashes, types, objects, and qids.

Role:
- Central contract for git command C files including `fs.c`, `get.c`, `delta.c`, config, pack, proto, ref, save, and utility modules.

Notable constraints:
- SHA-1 hash size is fixed at 20 bytes.
- Path buffers are mostly fixed-size Plan 9-style arrays.
