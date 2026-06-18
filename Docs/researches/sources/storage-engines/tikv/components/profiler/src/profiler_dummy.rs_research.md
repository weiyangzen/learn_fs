# sources/storage-engines/tikv/components/profiler/src/profiler_dummy.rs

Purpose: Provides the zero-cost fallback profiling API for builds where `profiling` is not enabled or the target is not Unix. It preserves API compatibility without bringing in profiling dependencies.

Important APIs/types/functions: `start(_name)` and `stop()` are both `#[inline]` public functions. `start` accepts any `AsRef<str>` to match the real backend signature and always returns `false`; `stop` also always returns `false`.

Control flow: Both functions return immediately. There is no backend detection, no locking, and no side effect.

State and persistence behavior: No state is stored and no profile output is produced.

Dependencies and integration points: It has no external dependencies. `src/lib.rs` re-exports this module when `not(all(unix, feature = "profiling"))`, allowing all callers to compile against profiler calls even in production-like builds.

Risks: Silent no-op behavior is deliberate but can surprise developers who forget to enable `--features profiling`. The return value is the only programmatic signal that profiling did not start or stop.

Test signals: Build coverage under default features confirms the dummy backend compiles. Behavior is simple enough that dedicated unit tests are not present.
