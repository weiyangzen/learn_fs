# sources/storage-engines/tikv/components/engine_traits/src/db_options.rs

Purpose: Defines generic database-wide option access, including rate limiting, flush behavior, Titan DB options, and WAL manifest verification.

Important APIs and control flow: `DbOptionsExt` associates `DbOptions` and provides get/set by string option pairs. `DbOptions` exposes max background jobs, rate limiter bytes and auto-tuning, flush size, flush-oldest-first, Titan DB options, and WAL manifest tracking. `TitanCfOptions` currently exposes construction and minimum blob size.

State, persistence, and dependencies: Implementations mutate live DB option state and may persist option changes through backend option files.

Integration points, risks, and test signals: Used by engine constructors, runtime config changes, and IO flow control. Risks include unsupported options, unit mismatches, option persistence drift, and Titan naming mismatch in `TitanCfOptions`. Constructor and backend option tests provide coverage.
