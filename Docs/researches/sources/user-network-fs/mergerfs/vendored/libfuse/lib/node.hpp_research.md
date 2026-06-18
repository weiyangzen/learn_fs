# sources/user-network-fs/mergerfs/vendored/libfuse/lib/node.hpp

## Purpose
`node.hpp` defines the compact node record used by the high-level FUSE namespace cache.

## Important APIs, Types, and Functions
`struct node_t` contains hash links for name/id tables, name string, parent pointer, node id, kernel lookup count, internal refcount, open count, remembered flag, stat-cache fingerprint, and tree lock counter. It declares `node_alloc`, `node_free`, `node_gc`, and `node_clear`. Static assertions pin the expected structure size on 64-bit and 32-bit builds.

## Control Flow
`fuse.cpp` embeds `node_t` in two hash tables: by node id and by `(parent,name)`. Lookup operations increment `nlookup`; forget operations decrement it. Open/release update `open_count`. Rename/unlink change name and parent links. Path resolution uses `treelock` to protect against concurrent tree mutation.

## State and Persistence
Every field is in-memory only. Node id values are exposed to the kernel for the active mount, but are regenerated after restart.

## Dependencies and Integration Points
This header is shared by `node.cpp` and `fuse.cpp`. Its layout affects memory usage and metrics reporting in `fuse.cpp`.

## Risks
Bitfield packing and static size assertions can fail across compilers/ABIs. Refcount, lookup count, open count, and treelock invariants are manually maintained. `name` ownership is external to the struct and must be freed exactly once.

## Test Signals
Compile on 32-bit/64-bit targets, stress lookup/forget/open/release/rename/unlink interactions, and verify metrics size expectations.
