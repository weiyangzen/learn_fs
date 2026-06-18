## sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/cpu.rs

Purpose: implements CPU usage sampling as a `SubRecorder`. It attributes per-thread CPU deltas to the currently attached resource tag.

Important APIs/types/functions: `CpuRecorder`, private `ThreadStat`, and `detect_thread_pool_type`. `thread_created` records the thread’s shared attached tag reference, initial stat, and detected pool type. `tick` reads current thread CPU stats, computes deltas from the previous sample, and calls `RawRecord::add_cpu_time` with the pool classification.

Control flow: each recorder tick iterates known thread stats, skips threads without an attached tag, reads current stats from `tikv_util::sys::thread`, increments `STAT_TASK_COUNT`, and updates the stored baseline. `resume` resets baselines to avoid charging paused time.

State/persistence: keeps an in-memory `HashMap<Pid, ThreadStat>`. `cleanup` retains only thread ids still present in recorder local-storage state and shrinks capacity above a threshold.

Dependencies/integration: depends on thread stat APIs, `THREAD_NAME_HASHMAP`, scheduler/unified read pool name matching, `RawRecords`, `ThreadPoolType`, and local storage shared tag state. Its output feeds reporter aggregation through raw record CPU fields.

Risks: CPU accounting is approximate and platform-specific; missing or stale thread names classify as `Unknown`; stat read failures skip samples; `u32` millisecond deltas can lose precision or saturate elsewhere depending on record merge behavior.

Test signals: platform-gated tests verify that CPU-heavy work under an attached tag creates records on Linux/macOS and that unsupported platforms leave records empty.
