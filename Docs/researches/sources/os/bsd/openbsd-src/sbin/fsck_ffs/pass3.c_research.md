# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/pass3.c

## Scope

Phase 3 for `fsck_ffs`: finds disconnected directories and attempts to reconnect orphaned directory subtrees through `lost+found`.

## Main APIs

- `pass3()` walks cached directories in reverse sorted order, detects directories not found from root, calls `linkup()`, updates parent/sibling relationships, and propagates reachability.

## Control Flow

For each directory except root, the pass skips already connected directories and clear-zero directories. For disconnected directories it walks up parent links until it finds an unparented directory, a parent not in `DSTATE`, or a loop guard exceeds `numdirs`. It then calls `linkup(orphan, inp->i_dotdot)`. On success, the reconnected directory’s parent and `..` are set to `lfdir`, `lost+found` link count is decremented, and the node is inserted into the `lost+found` child list. `propagate(orphan)` marks the recovered subtree.

## Dependencies

- Uses directory cache from pass 1 and parent data from pass 2.
- Depends on `linkup()` and `propagate()` from shared fsck directory code.
- Uses `lfdir` as the established lost+found inode.

## Risks And Edge Cases

- Loop detection is bounded by `numdirs`; malformed parent cycles beyond that are treated as orphan roots.
- Directories in `DCLEAR` are skipped because later cleanup handles them.
