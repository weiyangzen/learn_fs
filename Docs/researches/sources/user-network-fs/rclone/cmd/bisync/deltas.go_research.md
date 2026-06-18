# sources/user-network-fs/rclone/cmd/bisync/deltas.go

Purpose: Computes per-side changes since the last successful bisync listing and converts two delta sets into copy/delete/rename queues. It is the core decision engine for non-resync runs.

Important APIs/types/functions: `delta` is a bitmask for new, newer, older, larger, smaller, hash-different, and deleted states. `deltaSet` stores per-file delta bits plus changed size/time/hash values, counts for safety checks, and check-access files. `findDeltas` compares prior and current listings. `applyDeltas` resolves cross-side deltas into queued operations and calls copy/delete helpers. `excessDeletes` enforces max-delete. `updateAliases` supplements march aliases for deleted case/unicode variants.

Control flow: `findDeltas` loads the prior listing, validates old and current listings, iterates old files for deletion or modifications, then iterates current files for additions. It records at least one unchanged file to detect "all files changed" safety conditions. `applyDeltas` builds copy/delete/handled sets, loads directory-only listings when empty dir sync is enabled, batches potential same-name conflicts through `checkconflicts`, then iterates Path1 deltas and Path2 leftovers. Non-identical two-sided changes go through `resolve`; one-sided changes become copies or deletes. Finally it executes copy queues through `fastCopy` and directory synchronization through `syncEmptyDirs`; delete queues are saved for listing modification but actual deletion is represented by sync behavior and listing updates.

State and persistence behavior: Delta decisions depend on persisted `.path1.lst` and `.path2.lst` files plus newly written `-new` listings. Optional queue files are saved by `saveQueue` when `SaveQueues` is true. The function mutates `b.aliases` and `b.renames`, and returns `queues` used later by `modifyListing` to update persistent listings.

Dependencies and integration points: Depends on `fileList`, compare predicates, `bilib.Names`, filters, terminal logging, unicode normalization, `checkconflicts`, `resolve`, `listDirsOnly`, `fastCopy`, `retryFastCopy`, and `syncEmptyDirs`. It is called from `runLocked` after both current listings are built.

Risks: This is high-risk data movement logic. Alias handling for deleted files, case-insensitive remotes, and Unicode normalization is subtle. Equality checks skip files with definitely different size/hash, so stale or missing metadata can change conflict handling. Safety aborts rely on prior listings being trustworthy. Directory handling is intentionally different from file handling.

Test signals: Golden scenarios for changes, all_changed, max_delete, resolve, normalization, createemptysrcdirs, volatile, dry_run, and equal conflicts are key. Additional focused tests should cover deleted aliases, both-side delete, identical conflicts with differing modtime, missing hashes, and `--force` bypass behavior.
