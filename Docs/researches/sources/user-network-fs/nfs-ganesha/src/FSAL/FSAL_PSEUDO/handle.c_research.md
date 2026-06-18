# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/handle.c

## Purpose
Implements PSEUDO's in-memory directory handles and object operations: root lookup, mkdir, lookup, readdir, unlink, getattrs, handle serialization, and live-handle reconstruction.

## Important APIs, Types, and Functions
Helpers include `package_pseudo_handle`, `create_fullpath`, `alloc_directory_handle`, and AVL comparators. FSAL ops include `lookup`, `makedir`, `read_dirents`, `getattrs`, `file_unlink`, `handle_to_wire`, `handle_to_key`, `release`, `pseudofs_handle_ops_init`, `pseudofs_lookup_path`, and `pseudofs_create_handle`.

## Control Flow
Root lookup lazily creates the root for the export path. `makedir` allocates a child, packages a handle from full pseudo path, inserts it into parent name/index AVL trees, assigns a cookie index, and updates metadata. Lookup searches by name or `..`. Readdir walks index order. Unlink removes empty directories and marks them stale.

## State and Persistence Behavior
All namespace state is process memory. Each handle stores attributes, opaque handle bytes, parent pointer, child AVL trees, cookie counters, link count, name, and `inavl` liveness. No restart persistence exists.

## Dependencies and Integration Points
Depends on FSAL common helpers, CityHash, NFS handle sizing, display buffers, AVL trees, atomics, `op_ctx`, and export update status.

## Risks
Only directory behavior is implemented. Live linked handles are intentionally not freed on release. `pseudofs_create_handle` scans all live FSAL handles and cannot reconstruct evicted/nonresident handles. Handle uniqueness relies on hash plus truncated path bytes.

## Test Signals
Root lookup, mkdir/lookup/readdir, unlink empty/non-empty behavior, stale attrs after unlink, and handle-to-wire/create-handle round trips.
