# sources/object-store/rustfs/crates/io-core/examples/scheduler_example.rs

Purpose: demonstration binary for the public `rustfs-io-core` scheduler, buffer sizing, backpressure, deadlock detector, and lock optimizer APIs.

Important functions: `main` runs five examples. `io_scheduler_example` constructs an `IoSchedulerConfig`, creates an `IoScheduler`, and prints buffer choices for several file size, sequential/random, and media combinations. `buffer_size_example` demonstrates `calculate_optimal_buffer_size` and `get_buffer_size_for_media`. `backpressure_example` shows `BackpressureMonitor::with_defaults`, state checking, `try_acquire`, `release`, and counters. `deadlock_detection_example` registers locks, records holders and waits, and prints cycle detection. `lock_optimizer_example` records five synthetic lock acquisitions/releases and prints statistics.

Control flow and state: this is synchronous example code with stdout output only. It does not run real I/O; it simulates scenarios and lock events.

Dependencies and integration: imports the crate's public re-exports plus `StorageMedia` from `io_profile`. It validates that the library facade in `lib.rs` is usable from an external crate context.

Risks: examples can imply operational behavior stronger than the modules provide. The deadlock simulation records waits after both locks are held and should demonstrate cycle detection, but it does not model real thread IDs from runtime primitives. The scheduler example relies on functions from `scheduler.rs`, which is outside this work item.

Test signals: no assertions; this is a compile/run smoke example. Useful as API documentation, not correctness coverage.
