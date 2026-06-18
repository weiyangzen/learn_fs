# File Research: sources/os/plan9/plan9/sys/src/lib9p/file.c

This file implements lib9p’s in-memory `Tree`/`File` hierarchy used by simple tree-backed 9P servers.

Key behavior:
- Maintains a global free list of `File` objects allocated in batches.
- `alloctree` creates a root directory with uid/gid defaults and a destroy callback.
- `createfile` creates child files/directories, preserves creation order, assigns qids, initializes owner/mode/times, links into the parent, and returns a referenced file.
- `walkfile` and `walkfile1` resolve path elements and `..`, returning referenced files.
- `removefile` unlinks a leaf file from its parent, refuses root removal and non-empty directories, handles list tombstones, and drops tree/parent/caller refs.
- `opendirfile`, `readdirfile`, and `closedirfile` support stable directory iteration over the `Filelist`.
- `freetree` recursively destroys all files and frees the tree.

Important dependencies:
- Wire stat conversion via `convD2M`, relying on `File` layout embedding or matching `Dir` fields.
- Refcounting and locks from Plan 9 threading primitives.
- Destroy callbacks supplied by the embedding server.

Notable details:
- Locking rule is documented: lock child before parent; do not lock files while holding the free-file lock.
- Deleted entries remain as empty slots while directory readers exist, then `cleanfilelist` removes tombstones later.
- Directory qid/version bookkeeping is simple: qid paths come from `Tree.qidgen`; `Tree.dirqidgen` is initialized but not used in this file.
