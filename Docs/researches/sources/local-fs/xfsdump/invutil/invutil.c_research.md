# File Research: sources/local-fs/xfsdump/invutil/invutil.c

Implements the `xfsinvutil` command-line entry point and non-interactive inventory pruning logic. It parses options for interactive mode, force mode, fstab checking, mountpoint pruning, UUID pruning, session pruning, media-label filtering, debug, and lock waiting.

Core behavior:
- Initializes program/version globals and inventory base path through `inv_setup_base()`.
- Validates mutually exclusive option combinations.
- Parses prune dates with many accepted `strptime` formats and stores them as `time32_t`, with overflow detection.
- Traverses and prunes the inventory database hierarchy: `fstab` -> inventory index files -> storage object files.
- Uses mmap-backed in-place mutation for inventory files, then truncates or unlinks files when entries are removed.
- Uses advisory locking via `INVLOCK` in `open_and_lock()`.

Important functions:
- `main()` dispatches command mode.
- `ParseDate()` converts user dates to inventory-compatible 32-bit timestamps.
- `CheckAndPruneFstab()` removes duplicate fstab entries and entries whose index files become empty.
- `CheckAndPruneInvIndexFile()` removes inaccessible storage-object references and empty index files.
- `CheckAndPruneStObjFile()` marks sessions pruned based on date, session UUID, and optional media label.
- `uses_specified_mf_label()` limits pruning to sessions using a matching media label.
- `mntpnt_equal()` allows matching either full `host:path` strings or just mountpoint paths.

Dependencies:
- XFS inventory structs from `inv_priv.h`.
- `uuid_*` APIs for filesystem/session IDs.
- shared globals from `invutil.h`.
- `timeutil.h` for `ctime32`.

Notable risks/assumptions:
- Inventory files are treated as trusted binary layouts; mmap pointer arithmetic assumes valid offsets.
- Some allocations are unchecked, such as path construction helpers.
- Pruning modifies files in place and relies on locks to avoid xfsdump/xfsrestore races.
- `open_and_lock()` lock wait semantics depend on `INVLOCK` macro behavior.
- `CheckAndPruneStObjFile()` advances to the next `StObjhdr` after loop increment even on the last iteration, relying on mapped layout tolerance.
