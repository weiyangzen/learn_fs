# sources/storage-engines/tikv/components/tikv_util/src/thread_name_prefix.rs

Purpose: central registry of TiKV-owned thread name prefixes, ordered roughly by server startup sequence.

Important APIs/types/functions: many `pub const` prefixes plus `matches_thread_name_prefix` and `matches_scheduler_thread_name`. Matching handles full prefixes and Linux `comm` truncation to 15 visible bytes.

Control flow: callers pass an observed thread name and a prefix; long prefixes are checked both as full strings and truncated byte slices. The scheduler helper uses the generic `sched` prefix to cover multiple scheduler thread families.

State and persistence: stateless constants and pure matching helpers.

Dependencies/integration: consumed by thread builders, diagnostics, thread maps, profiling, and tests that identify TiKV threads by name.

Risks: byte slicing assumes ASCII prefixes; adding non-ASCII names would be unsafe. Over-broad scheduler matching intentionally accepts historical `scheduler-worker-pool` names.

Test signals: unit tests cover basic prefix matching, Linux truncation, and scheduler-name matching.
