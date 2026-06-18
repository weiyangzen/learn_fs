# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/dsl_bookmark.c

## Purpose

Implements ZFS bookmark lookup, creation, listing, and destruction in the DSL layer. Bookmarks are per-dataset ZAP entries that record a snapshot GUID, creation txg, creation time, and, for newer encrypted datasets, an IV-set GUID used by raw send/receive validation.

## Main Entry Points

- `dsl_bookmark_lookup()`: resolve `dataset#bookmark`, fetch bookmark physical data, and optionally verify timeline ancestry.
- `dsl_bookmark_create()`: batch create bookmarks through a sync task.
- `dsl_get_bookmarks()` / `dsl_get_bookmarks_impl()`: list bookmarks and requested properties.
- `dsl_bookmark_destroy()`: batch destroy bookmarks through a sync task.
- Internal helpers: `dsl_bookmark_hold_ds()`, `dsl_dataset_bmark_lookup()`, `dsl_dataset_bookmark_remove()`.

## Control Flow And State

`dsl_bookmark_hold_ds()` parses a full bookmark name around `#`, validates the bookmark component with `zfs_component_namecheck()`, and holds the containing dataset. Case-insensitive datasets use normalized ZAP lookup/removal.

Creation checks that the target source is a snapshot, the destination bookmark filesystem exists, the destination is in the snapshot's timeline, and the bookmark does not already exist. Sync creates the per-dataset bookmark ZAP lazily, increments `SPA_FEATURE_BOOKMARKS`, zapifies the dataset to store `DS_FIELD_BOOKMARK_NAMES`, writes a `zfs_bookmark_phys_t`, and logs history. For encrypted snapshots with bookmark-v2 support and a present `DS_FIELD_IVSET_GUID`, it stores the larger v2 record and increments `SPA_FEATURE_BOOKMARK_V2`.

Listing iterates the bookmark ZAP and emits only requested properties: GUID, createtxg, creation time, and IV-set GUID. Destroy treats nonexistent datasets/bookmarks as already destroyed, records successes in a temporary nvlist during check, removes entries in sync, decrements bookmark-v2 when removing larger entries, and destroys the bookmark ZAP plus feature reference when the last bookmark is removed.

## Dependencies

Depends on DSL dataset/dir holds, MOS ZAP objects, normalized ZAP operations for case-insensitive datasets, sync tasks, SPA feature reference counts, encryption IV-set metadata, property nvlist helpers, and name validation.

## Risks

Batch operations intentionally collect per-bookmark errors while returning an aggregate failure. Feature reference counts must match creation/destruction of bookmark ZAPs and v2-sized entries. Timeline validation via `dsl_dataset_is_before()` is required so bookmarks cannot be used as unrelated send origins. Older shorter bookmark records are supported by zeroing the output structure before lookup.
