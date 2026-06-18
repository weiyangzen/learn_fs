# Research: sources/object-store/minio/cmd/bucket-lifecycle-audit.go

Purpose: defines lifecycle audit event metadata for ILM operations. It wraps `lifecycle.Event` with a local source enum so audit and trace output can distinguish whether lifecycle work originated from healing, scanning, decom, rebalance, or an S3 request path.

Important APIs and types: `lcEventSrc` is a `uint8` enum with generated `String()` support from `stringer`; values include `lcEventSrc_Heal`, `lcEventSrc_Scanner`, `lcEventSrc_Decom`, `lcEventSrc_Rebal`, and S3 operation sources such as `lcEventSrc_s3PutObject`. `lcAuditEvent` embeds `lifecycle.Event` and stores `source lcEventSrc`. `Tags()` converts event fields into audit tag strings. `newLifecycleAuditEvent` is the constructor used by transition and expiry code.

Control flow: `Tags()` starts with a five-entry map, conditionally adds `ilm-src` when source is not `None`, always adds `ilm-action` and `ilm-rule-id`, and conditionally adds due time, transition tier, newer noncurrent versions, and noncurrent days. Time values use `iso8601Format`; integer values use `strconv.Itoa`.

State and persistence behavior: no persistent state is stored. The struct captures a snapshot of a lifecycle event and source for downstream audit logging.

Dependencies and integration points: depends on `internal/bucket/lifecycle` for event/action semantics and on generated stringer code for source names. It is consumed by `transitionObject`, `expireTransitionedObject`, and audit logging paths in lifecycle processing.

Risks: adding new `lcEventSrc` values requires regenerating stringer output or audit tags may degrade. Because tags are stringly typed, downstream dashboards depend on stable key names such as `ilm-action` and `ilm-tier`.

Test signals: no direct tests in this subset cover tag generation. Indirect coverage comes from lifecycle transition and expiry tests elsewhere if they assert audit output, but the local files mainly test lifecycle parsing and handlers.
