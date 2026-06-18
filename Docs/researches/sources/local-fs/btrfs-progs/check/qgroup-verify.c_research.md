# File Research: sources/local-fs/btrfs-progs/check/qgroup-verify.c

## Purpose
Implements quota-group verification, reporting, extent-root ownership tracing, and qgroup repair for `btrfs check`. It reconstructs expected qgroup referenced/exclusive counts from extent references and compares them with quota-tree `BTRFS_QGROUP_INFO_KEY` records.

## Main Data Model
- `struct qgroup_count` stores one qgroup id, whether its subvolume exists, on-disk counts, recomputed counts, parent/child qgroup relation lists, and a `bad_list` entry for repair.
- `counts` is a global rb-tree of `qgroup_count` records plus qgroup status flags: rescan, inconsistency, simple-quota mode, enable generation, and scan progress.
- `struct ref` stores one extent reference keyed by `(bytenr, parent, root)` in `by_bytenr`; full refs use `root`, shared refs use `parent`.
- `tree_blocks` is a ulist of interior tree blocks that need implied reference expansion for classic qgroups.

## Control Flow
- `qgroup_verify_all()` is the main verifier. It loads quota-tree qgroups and relations, scans all block groups' extent items, accounts extents, records bad qgroups, and returns `0`, positive inconsistency, or negative fatal error.
- `load_quota_info()` does two quota-tree passes: first reads status and qgroup info items, then reads relation items and links child qgroups to parent qgroups.
- `scan_extents()` walks extent-tree leaves over each block group range. It records inline refs, keyed refs, metadata item sizes, and interior tree blocks.
- Classic qgroups use `map_implied_refs()` and `account_all_refs()`: shared refs are recursively resolved to filesystem roots, then `account_one_extent()` propagates usage through qgroup parent relations.
- Simple quota mode bypasses classic backref resolution in `simple_quota_account_extent()` and accounts eligible extents directly to their owner root if the extent generation is not older than qgroup enable generation.

## Repair and Reporting
- `report_qgroups()` prints per-qgroup recomputed versus on-disk referenced/exclusive differences, with special messaging when rescan or inconsistency status makes differences expected.
- `repair_qgroups()` updates qgroup info items for all entries queued on `bad_qgroups`, then repairs the qgroup status item last so it gets the newest transaction id.
- `repair_qgroup_info()` writes recomputed referenced/exclusive and compressed counts into the quota tree.
- `repair_qgroup_status()` clears rescan/inconsistent state and preserves simple-quota status when applicable.

## Notable Behavior and Edge Cases
- Full refs are sorted before shared refs for a bytenr, which supports root resolution by walking a bytenr group from the leftmost node.
- Tree reloc self-reference loops are special-cased as `BTRFS_TREE_RELOC_OBJECTID` and skipped for qgroup contribution.
- `qgroup_seq` avoids clearing every qgroup refcount between extent-accounting rounds.
- `print_extent_state()` is a diagnostic path that prints extents and all roots referencing a chosen subvolume without updating qgroup counters.
- Global qgroup/ref state is intentionally retained until reporting, but `free_tree_blocks()` and `free_ref_tree()` clean transient scan state after each verification/debug pass.

## Dependencies
Uses btrfs core accessors, disk IO, transactions, ulist, extent IO, tree checker, rb-tree helpers, `check/repair.h`, and the public declarations in `check/qgroup-verify.h`.
