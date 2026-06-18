# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-mod-log.h

Declares the public interface and operation vocabulary for Btrfs tree modification logging.

Key declarations:
- `struct btrfs_seq_list` represents one active tree-mod-log user and stores its sequence number in a list node.
- `BTRFS_SEQ_LIST_INIT()` initializes a sequence-list element with `seq = 0`.
- `BTRFS_SEQ_LAST` is the sentinel maximum sequence value.
- `enum btrfs_mod_log_op` defines logged mutation kinds: key replace/add/remove, key remove while freeing, key remove while moving, key range move, and root replacement.
- Public APIs cover sequence acquisition/release, key/root/move/free/copy logging, rewinding an extent buffer, fetching an old root, querying an old root level, and obtaining the lowest active sequence.

Core mechanics:
- The header exposes only opaque `extent_buffer`, `btrfs_fs_info`, `btrfs_path`, and `btrfs_root` references, keeping log internals private to `tree-mod-log.c`.
- Callers pass `enum btrfs_mod_log_op` for key-level mutations so the implementation can store the old key pointer data and later replay the inverse operation.

Important invariants:
- A caller-owned `btrfs_seq_list` must have `seq == 0` before first registration if it expects to be inserted as a new blocker.
- Callers must eventually pair `btrfs_get_tree_mod_seq()` with `btrfs_put_tree_mod_seq()` so stale log entries can be reclaimed.
- The exported insertion helpers are intended for internal tree node/root structure changes, not data leaves.

Filesystem relevance:
- This header is the contract used by Btrfs tree manipulation code to preserve historical metadata views for backref and extent logic.

Notable risks:
- Misusing operation types at call sites can make rewind apply the wrong inverse operation.
- Forgetting to release a sequence blocker can pin tree modification log memory.
