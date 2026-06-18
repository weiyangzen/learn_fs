# sources/security-integrity/cryfs/crates/utils/src/lazy_reclaim.rs

Purpose: lazily initialized shared value that is reclaimed when no `Arc` references remain and recreated on later demand.

Important APIs/types/functions: `LazyReclaim<T> { inner: Mutex<Weak<T>>, init: fn() -> T }`; `const fn new(init)` and `get_or_init`.

Control flow: `get_or_init` locks the weak pointer, attempts `upgrade`, and if it fails creates a new `Arc`, stores a downgraded weak pointer, and returns the new strong reference.

State/persistence: only a `Weak` is retained by the lazy container; actual value lifetime is controlled by external `Arc` holders.

Dependencies/integration: useful for reclaimable caches, pools, or expensive resources.

Risks: init function is a plain `fn`, not a capturing closure. Mutex poisoning panics. A new instance may be created after all references drop, so identity is not stable forever.

Test signals: unit tests cover value access, same instance while held, reinitialization after drop, partial reference retention, static use, and thread safety.
