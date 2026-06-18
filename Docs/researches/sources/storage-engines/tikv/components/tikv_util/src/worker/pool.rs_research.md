# sources/storage-engines/tikv/components/tikv_util/src/worker/pool.rs

Purpose: YATP-backed worker pool abstraction for synchronous `Runnable` tasks, optional periodic timeouts, lazy workers, and generic async tasks.

Important APIs/types/functions: `ScheduleError`, `Runnable`, `RunnableWithTimer`, `Scheduler`, `LazyWorker`, `ReceiverWrapper`, `Builder`, and `Worker`.

Control flow: schedulers maintain an atomic pending counter and unbounded channel. `schedule` enforces `pending_capacity`; `schedule_force` bypasses it but still increments metrics and counter. `Worker::start_with_timer_impl` spawns an async loop in `FuturePool`, dispatching `Msg::Task` to `run` and `Msg::Timeout` to `on_timeout`, rescheduling timeouts via `GLOBAL_TIMER_HANDLE`.

State and persistence: in-memory YATP pool, atomics for stop/pending count, Prometheus metrics, and channels. `RunnableWrapper::drop` invokes `shutdown`.

Dependencies/integration: built on `yatp_pool::FuturePool`, global timer, Prometheus worker metrics, and TiKV future helpers.

Risks: pending counter is decremented only after `run`; panics can poison accounting. Timeout messages share the same channel as tasks and may be delayed behind workload. `is_busy` uses pending count versus core thread count, not actual executor availability.

Test signals: tests cover lazy timer workers, capacity failures, shutdown callbacks, interval timeout behavior, and handled-task metrics.
