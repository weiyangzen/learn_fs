# sources/storage-engines/tikv/components/engine_panic/src/io_limiter.rs

Purpose: Panic skeleton for engine I/O limiter support.

Important APIs and types: `PanicEngine` implements `IOLimiterExt` with associated `PanicIOLimiter`; `PanicIOLimiter` implements constructor, rate setter, request accounting, and metric getters.

Control flow and state: Every method panics. There is no limiter state.

Dependencies and integration: Tracks `engine_traits::{IOLimiter, IOLimiterExt}`.

Risks: Runtime use panics.

Test signals: No tests.
