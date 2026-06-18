# sources/object-store/rustfs/crates/obs/src/metrics/schema/audit.rs

Purpose: defines audit target metric descriptors and shared status/result label constants.

Important APIs/types: constants `RESULT`, `STATUS`, `SUCCESS`, and `FAILURE`; private `TARGET_ID`; descriptors `AUDIT_FAILED_MESSAGES_MD`, `AUDIT_TARGET_QUEUE_LENGTH_MD`, and `AUDIT_TOTAL_MESSAGES_MD`.

Control flow: each descriptor is a `LazyLock<MetricDescriptor>` initialized through `new_counter_md` or `new_gauge_md` with `subsystems::AUDIT` and `target_id` label.

State/persistence: descriptors are lazily initialized process-wide. No mutable state after initialization.

Dependencies/integration: audit collector uses these descriptors to convert audit target snapshots, and scheduler obtains raw snapshots from `rustfs_audit::audit_target_metrics`.

Risks: `TARGET_ID` is private while descriptors include it, so collectors in other modules cannot import the label constant from schema and may duplicate the string unless specifically designed around it. Public `RESULT/STATUS/SUCCESS/FAILURE` are not used in this file's descriptors, suggesting broader audit schema usage or leftovers.

Test signals: no local tests; collector tests and compile-time descriptor use provide indirect coverage.
