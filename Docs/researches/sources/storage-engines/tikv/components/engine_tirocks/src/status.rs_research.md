# sources/storage-engines/tikv/components/engine_tirocks/src/status.rs

Purpose: Converts between TiRocks status objects and the engine-trait error/status model.

Important APIs and control flow: `to_engine_trait_status` maps TiRocks `Code`, `SubCode`, `Severity`, and optional byte state into `engine_traits::Status`. `r2e` wraps TiRocks status as `Error::Engine`. `e2r` maps engine-trait errors back to TiRocks status, using `kIOError` for non-engine errors.

State, persistence, and dependencies: No persistent state is held; this is an error boundary between TiRocks and generic TiKV engine users.

Integration points, risks, and test signals: Used throughout TiRocks adapters for `map_err(r2e)` and callback error conversion. Risks include enum drift, `unreachable!` if TiRocks exposes a new max/sentinel variant unexpectedly, lossy conversion of non-engine errors to IO errors, and UTF-8 lossiness for TiRocks state bytes. Test signals are mostly compile-time exhaustiveness plus any runtime engine error assertions in trait tests.
