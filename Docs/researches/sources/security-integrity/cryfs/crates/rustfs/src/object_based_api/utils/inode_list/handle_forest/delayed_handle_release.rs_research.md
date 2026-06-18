# sources/security-integrity/cryfs/crates/rustfs/src/object_based_api/utils/inode_list/handle_forest/delayed_handle_release.rs

Purpose: RAII guard ensuring removed handles are intentionally released back to a `HandleForest` only after associated async drops complete.

Important APIs: `DelayedHandleRelease::new`, `release`, and `Drop`.

Control flow and state: stores `Option<Handle>`. `release` consumes the guard and calls `forest.release_removed_handle`. If dropped without release, `safe_panic!` reports an invariant violation.

Dependencies and integration: returned by `HandleForest::try_remove` and used by `InodeList` to delay inode-number reuse until `ConcurrentStore` entries are absent.

Risks and tests: forgetting to call `release` causes a panic-like safe failure, preventing silent handle leaks or unsafe reuse. It assumes release is always paired with the original forest.
