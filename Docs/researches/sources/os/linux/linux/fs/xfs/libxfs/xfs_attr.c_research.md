# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr.c

## Purpose
Implements the main XFS extended attribute API and the delayed attribute operation state machine. It routes lookups, creates, replaces, and removals across shortform inode-local attributes, single leaf blocks, and multi-block node/Btree attr forks.

## Main Interfaces
- Attribute queries: `xfs_attr_get()`, `xfs_attr_get_ilocked()`, `xfs_inode_hasattr()`, `xfs_attr_is_leaf()`.
- Attribute mutations: `xfs_attr_set()`, `xfs_attr_set_iter()`, `xfs_attr_setname()`, `xfs_attr_removename()`, `xfs_attr_replacename()`.
- Format/space helpers: `xfs_attr_calc_size()`, `xfs_attr_set_resv()`, `xfs_attr_add_fork()`, `xfs_attr_sf_totsize()`.
- Hash/name validation: `xfs_attr_hashname()`, `xfs_attr_hashval()`, `xfs_attr_namecheck()`, `xfs_attr_check_namespace()`.
- Intent cache lifecycle: `xfs_attr_intent_init_cache()`, `xfs_attr_intent_destroy_cache()`.

## Control Flow
`xfs_attr_get()` initializes `xfs_da_args`, computes the namespace-aware hash, takes an attr-map shared lock, and calls `xfs_attr_get_ilocked()`. The locked getter loads attr-fork extents and chooses shortform, single-leaf, or node lookup based on fork format and `xfs_attr_is_leaf()`.

`xfs_attr_set()` calculates reservations for create/replace/upsert or remove, creates the attr fork if needed, allocates an inode transaction, checks extent-count growth, performs an initial lookup, and dispatches to set, replace, or remove helpers. Shortform operations can complete immediately in one transaction; larger operations are queued through deferred attr intents.

`xfs_attr_set_iter()` drives resumable delayed operations through `enum xfs_delattr_state`. It handles shortform add/remove, leaf add/remove, node add/remove setup, remote value space discovery/allocation, incomplete-flag flips for atomic replace, remote block invalidation/removal, leaf entry removal, node cleanup, and optional leaf-to-shortform shrinking.

## State And Transactions
The file relies on `struct xfs_attr_intent` to carry current DA state, saved DA lookup state, remote extent allocation progress, and operation flags across transaction rolls. Remote attribute replacement uses saved `blkno/index/rmtblk*` fields to distinguish old and new entries. `XFS_ATTR_INCOMPLETE` is used to hide partially created or replaced attributes from normal lookup until remote values are durable and flags are flipped or cleared.

## Integration Points
Calls shortform and leaf routines from `xfs_attr_leaf.c`, remote value routines from `xfs_attr_remote.c`, DA Btree helpers from `xfs_da_btree`, bmap attr-fork helpers, transaction reservation tables, deferred operation logging in `xfs_attr_item`, quota and inode transaction allocation, and parent-pointer hash/name validation through `xfs_parent`.

## Notable Behaviors
- Parent-pointer attributes use `xfs_parent_hashattr()` and have special replace handling that swaps canonical name/value fields after removal.
- Logged attribute replacement starts with removal for crash recovery consistency; unlogged replacement normally adds first and then atomically flips incomplete flags.
- Leaf and node remote values are allocated after the leaf entry exists to avoid oversized transactions and deadlocks.
- Recovery remove paths tolerate missing attributes as successful cleanup.
- Namespace validation enforces at most one on-disk namespace bit per attribute, while parent-pointer names delegate to parent-specific validation.

## Risks And Review Focus
- State transitions in `xfs_attr_set_iter()` must remain aligned with `enum xfs_delattr_state`; several paths depend on sequential leaf/node state ordering.
- Atomic replace correctness depends on preserving old versus new entry locations through splits and transaction rolls.
- Remote value removal and incomplete-flag handling are crash-consistency sensitive.
- Shortcut shortform replacement must fall back cleanly when size changes force leaf conversion.
