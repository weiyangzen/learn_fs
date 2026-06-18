# sources/storage-engines/tikv/components/engine_panic/src/db_options.rs

Purpose: Panic skeleton for database-wide options and Titan DB options.

Important APIs and types: `PanicEngine` implements `DbOptionsExt` with `PanicDbOptions`. `PanicDbOptions` implements rate limiter, flush size, background jobs, WAL manifest verification, and Titan option hooks. `PanicTitanDbOptions` implements `TitanCfOptions`.

Control flow and state: Every getter/setter panics; no option state is stored.

Dependencies and integration: Tracks `engine_traits::{DbOptions, DbOptionsExt, TitanCfOptions}`.

Risks: Runtime use panics; compile success keeps the engine skeleton synchronized with option trait evolution.

Test signals: No tests.
