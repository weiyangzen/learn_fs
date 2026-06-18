# sources/user-network-fs/rclone/cmd/bisync/resolve.go

Purpose: Defines automatic conflict-resolution strategies and loser actions for files changed on both sides, including conflict suffix generation, winner selection, renaming, deletion, and rename bookkeeping for listing updates.

Important APIs/types/functions: `Prefer` enum supports none, path1, path2, newer, older, larger, and smaller. `ConflictLoserAction` supports numbered suffix, pathname suffix, and delete. `setResolveDefaults` validates suffix and strategy compatibility. `renames`, `renamesInfo`, and `namePair` record old/new names. `resolve`, `SuffixName`, `numerate`, `numerateSingle`, `rename`, `delete`, `conflictWinner`, `resolveNewerOlder`, and `resolveLargerSmaller` implement behavior.

Control flow: For a two-sided non-identical change, `resolve` optionally picks a winning path, computes default suffixed names, adjusts names for pathname or numbered/delete loser policies, and either deletes the loser plus queues winner copy or renames both/non-winner files and queues copies of renamed objects. Numbering probes both listings and aliases until an unused suffix is found. Rename and delete operations honor dry-run/destructive skip checks. The rename map is stored for later listing reconciliation.

State and persistence behavior: Conflict resolution can mutate remote state immediately via `operations.MoveFile` or `DeleteFileWithBackupDir`, with path-specific backup-dir config. It mutates `b.renames`, copy queues, and `renameSkipped`; durable listing state is updated later in `modifyListing`. Suffixes may include expanded time globs captured once per run.

Dependencies and integration points: Called from `applyDeltas`; relies on delta metadata, listing alias maps, fs config `SuffixKeepExtension`, transform suffix/time helpers, rclone destructive-operation safeguards, backup-dir setup, and listing update code.

Risks: Conflict handling is destructive and user-visible. Winner selection can be indeterminate when modtime/size data is missing or equal. Delete-loser only deletes when a winner is known; otherwise both sides are renamed. Naming must account for aliases, case-insensitive remotes, unicode normalization, and extension-preserving suffixes. Errors during rename/delete are critical.

Test signals: `test_resolve`, `test_resync_modes`, normalization/fix-case cases, and backupdir cases are central. Focused tests should cover suffix parsing with one/two/more values, suffix-keep-extension, numbered collision search, no-winner delete fallback, path1/path2/newer/older/larger/smaller winners, and dry-run skip behavior.
