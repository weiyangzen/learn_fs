# sources/storage-engines/tikv/components/tikv_util/src/timer.rs

Purpose: timer utilities for sorted timeout tasks and global Tokio 0.1 timer handles, including a steady timer insulated from wall-clock adjustment.

Important APIs/types/functions: `Timer<T>`, `GLOBAL_TIMER_HANDLE`, `SteadyClock`, `SteadyTimer`, `RatchetClock`, and `start_timer_thread`.

Control flow: `Timer<T>` stores `TimeoutTask`s in a `BinaryHeap<Reverse<_>>` and pops tasks due before a supplied `Instant`. Global timer threads run `tokio_timer::Timer::turn` forever and return handles over a channel. `RatchetClock` clamps backwards movement at millisecond precision to avoid tokio-timer panics.

State and persistence: in-memory heaps, lazy-static global handles, and a background thread per global timer. Thread group properties are copied into timer threads.

Dependencies/integration: used by worker intervals, future workers, YATP cleanup tasks, and delay futures. Depends on `tokio_timer`, `tokio_executor`, and TiKV clock utilities.

Risks: timer threads are intentionally never joined; clock-family mismatches in `TimeoutTask` ordering would panic; `SteadyClock` instants are only comparable within the same zero origin.

Test signals: unit tests cover ordered task popping, global timer delay, steady delay, and ratchet behavior under an intentionally backward-moving clock.
