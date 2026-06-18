# sources/user-network-fs/rclone/cmd/bisync/listing.go

Purpose: Defines bisync's persisted listing format and the machinery for loading, saving, validating, updating, rechecking, and rolling back `.lst` files. These listings are the durable state that lets later runs detect changes on each side.

Important APIs/types/functions: `ListingHeader`, `lineFormat`, `lineRegex`, `timeFormat`, `TZ`, and `LogTZ` define serialization. `fileInfo` and `fileList` store remote name to size/time/hash/id/flags data. Core methods include `has`, `get`, `put`, `remove`, `save`, `loadListing`, `fileInfoEqual`, `checkListing`, `listDirsOnly`, `modifyListing`, `recheck`, `rollback`, `prepareRollback`, `getOldLists`, and generic `Concat`.

Control flow: New listings are created during march or resync. `save` sorts remote names, writes a header, and serializes entries with optional hash type prefix. `loadListing` parses lines defensively, skipping malformed and inconsistent-hash lines, and keeps the newest duplicate. `modifyListing` loads source/destination listings, derives winners and errors from sync `Results`, removes or adds queued files, applies rename bookkeeping, rechecks uncertain files with narrow filters, handles graceful-shutdown rollback, then saves both listings. `recheck` lists selected source/destination objects and uses `WhichEqual` before trusting listing updates; unresolved items roll back to `-old` listings outside resync.

State and persistence behavior: Listing files are persistent state: current `.lst`, temporary `.lst-new`, backup `.lst-old`, dry-run `.lst-dry`, and failure `.lst-err` names are managed elsewhere but parsed here. `saveOldListings`, `replaceCurrentListings`, and `revertToOldListings` copy listing generations. Directory entries are represented with flag `d` and size `-1` when empty-dir sync is enabled. Timezone for persisted times is controlled by `TZ`.

Dependencies and integration points: Used by every bisync mode. Integrates with `bilib.CopyFileIfExists`, rclone filter/list operations, hash APIs, accounting transfer stats, `Results` from `queue.go`, alias and rename maps from delta resolution, and comparison logic from `compare.go`.

Risks: Listing correctness is central to data safety. Malformed lines are ignored rather than fatal, which can hide partial corruption. Duplicate handling keeps the latest modtime. Hash type consistency is enforced per listing, so mixed hash listings lose lines. `modifyListing` must reconcile copies, renames, skipped equal conflicts, empty dirs, dry-run, and graceful shutdown without losing retry state.

Test signals: Most golden tests compare final and saved listings. Important scenarios include dry_run, check_sync, resync, resolve, createemptysrcdirs, rmdirs, normalization, and volatile shutdown/concurrent mutation. Focused tests should cover parsing malformed listings, duplicate entries, rollback from old listings, recheck failures, and mixed hash types.
