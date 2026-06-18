# sources/security-integrity/cryfs/crates/utils/src/testutils/static_drop.rs

Purpose: Implements `StaticDrop<T>`, a test-focused wrapper that runs `Drop` for values stored in Rust statics at process exit. It addresses lazy static resources such as `TempDir` or child-process handles whose destructors would otherwise be skipped.

Important APIs and types: `StaticDrop::new(value)` registers a heap-stable `T`; `Deref` exposes `&T`; `Drop` deregisters normally dropped wrappers. Private global state is `REGISTRY: Mutex<Vec<Entry>>`, where `Entry` stores a type-erased pointer and an unsafe drop function. The `cleanup_leaked_statics` function is registered with `dtor::dtor(unsafe, method = at_binary_exit)`.

Control flow: Construction boxes `T`, stores the raw pointer and a monomorphized drop closure in the registry, and returns the wrapper. Normal `Drop` finds its pointer in the registry, removes it with `swap_remove`, then manually drops the box. At binary exit, the destructor takes the entire registry, iterates remaining entries, and invokes each drop function inside `catch_unwind` so one panicking destructor does not prevent later cleanup.

State and persistence behavior: State is process-global registry memory plus each wrapper's heap allocation. Exit-time cleanup can cause filesystem or process side effects depending on `T::drop`. It is registered through `atexit`, so it runs on normal return and `std::process::exit`, but not abort, `_exit`, or hard signals.

Dependencies and integration points: Uses `dtor`, `Mutex`, `ManuallyDrop`, raw pointers, and lazy-static patterns such as `LazyLock`. It is intentionally in `testutils` and documented as not a production resource ownership pattern.

Risks: The implementation uses unsafe type-erased drop pointers; correctness relies on the boxed allocation remaining stable and each entry being dropped exactly once. There is no ordering guarantee among static drops or with other live threads at process exit. Async cleanup is unsupported. Signal-based exits do not run this destructor.

Test signals: Unit tests validate normal drop, deref behavior through `LazyLock`, move stability, independent registry entries, `Send`/`Sync` bounds, and no double-drop after normal cleanup. Integration tests in this subset verify process-exit behavior and panic isolation.

Source-read signal: Read `sources/security-integrity/cryfs/crates/utils/src/testutils/static_drop.rs` completely for this pass (269 lines, 10588 bytes).
