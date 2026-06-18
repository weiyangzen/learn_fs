# sources/user-network-fs/rclone/cmd/bisync/resync.go

Purpose: Implements `--resync` and `--resync-mode`, the recovery/initialization mode that rebuilds listings by copying unique or preferred files across both paths before normal incremental bisync can run.

Important APIs/types/functions: `setResyncDefaults` maps legacy `--resync` to `--resync-mode path1` and validates mode support. `resync` runs the two directional copy passes and listing updates. `setResyncConfig` maps resync modes to rclone sync config for path preference/newer behavior. `resyncWhichIsWhich` and `resyncWinningPathToEqual` support custom equality for older/larger/smaller modes.

Control flow: `resync` first writes blank `-new` listings, optionally runs check-access through `findCheckFiles`, then copies Path2 to Path1 and Path1 to Path2 using `resyncDir`. For path preference modes it toggles `IgnoreExisting` between the two passes. For newer it enables `UpdateOlder`; older/larger/smaller are implemented by the equality override in `checkfn.go`. It replaces current listings, derives queues from successful source-side results, calls `modifyListing` for both directions, optionally validates check-sync, and removes temporary new listings unless `NoCleanup`.

State and persistence behavior: Resync creates or replaces durable `.path1.lst` and `.path2.lst` from scratch, saving old listings when present. It writes temporary blank listings to seed `modifyListing`. It respects dry-run through context config and leaves temp files when cleanup is disabled.

Dependencies and integration points: Called from `runLocked` before normal prior-listing checks. Uses queue/resyncDir, listing modification, check-access, check-sync, backup-dir setup, and conflict preference enums from `resolve.go`.

Risks: Resync intentionally establishes the baseline truth, so wrong preference logic can overwrite desired versions. Two-pass copy behavior is sensitive to `IgnoreExisting`, `UpdateOlder`, and custom equality semantics. Check-access is enforced even during resync, which can block recovery if check files are unavailable.

Test signals: `test_resync` and `test_resync_modes` cover the main behavior; check-access and dry-run scenarios add cross coverage. Focused tests should assert mode defaults, unsupported modtime/size fallback to path1, two-pass queue derivation, and final listing equality.
