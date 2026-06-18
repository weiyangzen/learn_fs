# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfeature.c

## Role
Implements pool feature-flag bookkeeping for ZFS on-disk format features. It checks feature compatibility, reads/caches feature refcounts, enables features and dependencies, updates active reference counts, creates feature ZAP objects, and records enabled txg metadata.

## Feature Model
- Features are disabled when absent from feature ZAPs, enabled with refcount 0, and active with refcount greater than 0.
- Readonly-compatible features are stored in `features_for_write`; other active read-required features are stored in `features_for_read`.
- Descriptions are stored in `feature_descriptions`.
- Some active read-required features are also written to labels so compatibility can be checked before opening MOS feature ZAPs.

## Compatibility And Refcounts
- `spa_features_check()` walks the relevant feature ZAP, optionally records enabled features, and reports unsupported active features with descriptions.
- `feature_get_refcount()` reads the in-memory `spa_feat_refcount_cache`, returning `ENOTSUP` for disabled features.
- `feature_get_refcount_from_disk()` reads the relevant feature ZAP directly and treats missing entries as disabled.
- `feature_get_enabled_txg()` retrieves a feature's enabling txg from `spa_feat_enabled_txg_obj` when the feature depends on `SPA_FEATURE_ENABLED_TXG`.

## Sync/Enable Operations
- `feature_sync()` updates the feature ZAP refcount, atomically updates the in-memory cache for normal registered features, and activates/deactivates MOS feature tracking depending on refcount and feature flags.
- `feature_enable_sync()` ignores already-enabled features, recursively enables dependencies, writes description, initializes refcount to 1 for activate-on-enable features or 0 otherwise, records enabled txg if that feature is active, and handles the specific encryption/bookmark_v2 errata repair case.
- `feature_do_action()` increments or decrements an enabled feature refcount in syncing context and calls `feature_sync()`.
- `spa_feature_create_zap_objects()` creates the three feature ZAP objects in the pool directory during pool creation or upgrade.
- `spa_feature_enable()`, `spa_feature_incr()`, and `spa_feature_decr()` are the public wrappers.

## Query APIs
- `spa_feature_is_enabled()` checks version support and refcount-cache presence.
- `spa_feature_is_active()` additionally requires nonzero refcount.
- `spa_feature_enabled_txg()` returns whether the feature is enabled and, if so, the txg in which it was enabled.

## Important Details
- Refcount updates are only valid in syncing context.
- `feature_sync()` is intentionally non-static for `zhack`, and handles arbitrary feature guids by skipping cache updates when `fi_feature == SPA_FEATURE_NONE`.
- Enabling a feature must not perform feature-specific on-disk initialization; individual feature users create metadata on first use and increment/decrement active refcounts.
- Dependencies are enable-time only; disabling is not implemented here.
