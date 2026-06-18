# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfeature.h

This header declares SPA feature-flag management over the MOS feature ZAP objects.

Core definitions:
- `VALID_FEATURE_FID()` validates feature IDs against `SPA_FEATURES`.
- `VALID_FEATURE_OR_NONE()` also permits `SPA_FEATURE_NONE`.

Public API surface:
- Create feature ZAP objects, enable a feature, increment/decrement feature refcounts, query enabled/active/enabled-TXG/refcount state, and check feature compatibility for import/read-write use.
- Lower-level `feature_get_refcount()`, disk refcount retrieval, `feature_enable_sync()`, and `feature_sync()` are exported for `zhack` and `zdb`, not normal callers.

Risk-sensitive invariants:
- Feature enablement and refcounts are persistent compatibility gates for pool import and write support.
- Normal callers should use SPA feature APIs rather than low-level feature sync helpers.
