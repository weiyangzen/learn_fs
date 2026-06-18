# File Research: sources/os/plan9/9front/sys/src/lib9p/file.c

## Read Status
Complete: 425 lines read.

## Purpose
Implements lib9p’s in-memory `Tree` and `File` hierarchy helpers. This gives 9P servers a default file tree model with creation, walking, removal, stat data, reference management, and directory iteration.

## Main Responsibilities
- Allocate and recycle `File` objects.
- Maintain parent/child relationships through linked `Filelist` entries.
- Preserve creation order during directory iteration.
- Safely remove files while active directory readers may still reference list nodes.
- Provide path walking helpers.
- Build and free whole trees.
- Provide directory open/read/close helpers for server reads.

## Important Functions
- `allocfile`, `freefile`: internal file allocator/free-list management.
- `createfile`: creates a child under a directory, assigns qid path/type, ownership, mode, and timestamps.
- `removefile`: removes a leaf file from its parent and handles reference release.
- `walkfile1`, `walkfile`: walk one path element or slash-separated paths.
- `alloctree`: creates a root directory tree with ownership and mode.
- `freetree`, `_freefiles`: recursively destroy a tree.
- `opendirfile`, `readdirfile`, `closedirfile`: support serialized directory reads.

## Data Structures
- `Filelist`: linked child entry, possibly retained with `f == nil` while readers exist.
- `Readdir`: directory read cursor containing a directory and current `Filelist` position.
- `Tree`: holds root file, qid generator, and destroy callback.

## Dependencies and Interactions
- Used by `srv.c` when `srv->tree` is set.
- `convD2M` serializes `File` directory metadata into 9P stat records.
- `hasperm` from `uid.c` checks permissions for open/create/remove paths.
- Lock ordering is explicitly documented: lock child before parent; do not lock files while holding the free-file lock.

## Notes
- Removed children are marked empty first, then list entries are cleaned only when no directory readers remain.
- `closefile` invokes the tree destroy callback when the final reference disappears.
