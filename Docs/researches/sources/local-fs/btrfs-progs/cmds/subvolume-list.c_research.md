# File Research: sources/local-fs/btrfs-progs/cmds/subvolume-list.c

## Purpose

Implements `btrfs subvolume list`, collecting subvolume/snapshot root metadata through tree-search ioctls, resolving paths, applying filters/sorters, and printing default/table/raw/JSON layouts.

## Main Data Structures

- `struct root_info`: one root/subvolume record with root id, refs, generation, creation generation/time, flags, UUIDs, name, path, full path, and deleted marker.
- `struct btrfs_list_filter_set`: dynamic array of predicates.
- `struct btrfs_list_comparer_set`: dynamic array of sort comparers.
- Two rbtrees are used:
  - lookup tree keyed by root id
  - sorted output tree keyed by configured comparers plus root id fallback

## Control Flow

1. `cmd_subvolume_list()` parses field, filter, sort, and layout options.
2. Opens the path and resolves the current top root id.
3. `list_subvol_search()` searches the root tree for `ROOT_ITEM` and `ROOT_BACKREF` items, adding/updating `root_info` records.
4. `lookup_ino_path()` asks the kernel to resolve each root reference directory path.
5. `resolve_root()` walks parent root references to assemble full paths.
6. Deleted or unresolved roots are marked with `DELETED`; top-level gets `TOPLEVEL`.
7. Filters are applied, then records are inserted into the sorted rbtree.
8. Output is printed in default, table, raw, or JSON form.

## Filters And Sorting

Filters include root id, snapshots only, readonly flags, generation comparisons, creation generation comparisons, top-id equality, full-path display adjustment, parent UUID, and deleted-only mode.

Sort keys include root id, generation, creation generation, and path, each optionally ascending or descending.

## Dependencies

Uses Btrfs tree-search and inode-lookup ioctls, rbtrees, UUID formatting/comparison, command formatting helpers, and subvolume command definitions.

## Risks And Edge Cases

- Several allocation failures call `exit(1)` instead of returning errors.
- `filter_by_parent()` stores a UUID pointer through a `u64` data field cast, which is pointer-size dependent and not type-safe.
- Path reconstruction depends on root backrefs and inode lookup; deleted or missing parents become `DELETED`.
- `comp_entry_with_path()` assumes `full_path` is populated before sorting by path; this is satisfied by current `filter_and_sort_subvol()` ordering.
- The top-level subvolume is collected but skipped in normal printing.
