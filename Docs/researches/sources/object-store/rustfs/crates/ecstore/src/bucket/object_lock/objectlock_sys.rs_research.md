# sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/objectlock_sys.rs

Purpose: Implements object-lock enforcement decisions for deletion and retention modification. It combines explicit object metadata with bucket default retention from metadata_sys.

Important APIs and types: `BucketObjectLockSys::get` returns a bucket's `DefaultRetention`. `is_retention_active` validates mode and future retain-until date. `check_retention_for_modification` enforces S3 semantics for COMPLIANCE and GOVERNANCE changes. `add_years` handles leap-day rollover. `is_object_locked_by_metadata` is a synchronous metadata-only check. `ObjectLockBlockReason` distinguishes `LegalHold` and `Retention` with user-facing messages. `check_object_lock_for_deletion` is the full async deletion gate.

Control flow and state: Delete markers bypass locks. Legal hold ON always blocks deletion. Explicit retention is evaluated before bucket default retention. COMPLIANCE cannot be shortened, cleared, or mode-changed; GOVERNANCE can be shortened or changed only with bypass. Default retention computes retain-until from `ObjectInfo.mod_time` plus configured days or years.

Dependencies and integration: Reads bucket default object-lock config through `metadata_sys::get_object_lock_config`, parses metadata through `objectlock.rs`, and consumes `store_api::ObjectInfo`.

Risks: Default retention is ignored when object modification time is absent. Bypass permission is assumed to be checked by the caller that passes `bypass_governance`. `check_retention_for_modification` compares `new_mode != Some(mode_str)`, so callers must pass canonical DTO strings to avoid false mode-change detection.

Test signals: Extensive unit tests cover year arithmetic, active/expired retention, compliance and governance modification semantics, legal holds, delete-marker behavior, and metadata-only lock checks. Async default-retention deletion behavior is not directly tested here.
