# sources/storage-engines/tikv/components/tikv_util/src/time.rs

Purpose: TiKV time utility layer for monotonic clocks, Unix time conversion, slow-operation timers, time-jump monitoring, read stream IDs, and coarse-clock integration with `async_speed_limit`.

Important APIs/types/functions: `Timespec`, `Instant`, `UnixSecs`, `SlowTimer`, `Monitor`, `CoarseClock`, `Limiter`, `ThreadReadId`, conversion helpers, `setup_for_spin_interval`, and `spin_at_least`.

Control flow: Linux paths call `clock_gettime` for monotonic, raw, and coarse clocks; non-Linux paths emulate with a process-local `std::time::Instant` origin. `Instant` refuses comparisons across monotonic/coarse variants except equality false and `partial_cmp(None)`. `Monitor` periodically samples `SystemTime` and calls `on_jumped` if wall time moves backward.

State and persistence: no persistence. TLS stores per-thread read sequence; static mutable spin calibration is initialized once; monitor owns a background thread and shutdown channel.

Dependencies/integration: used by metrics, timers, scheduling, rate limiting, and transaction timestamp-related wall-clock helpers.

Risks: duration conversion can overflow for huge inputs; `to_std_duration` unwraps and therefore rejects negative `time::Duration`; static mutable spin calibration is intentionally guarded by `Once` but still unsafe.

Test signals: tests cover time monitor callbacks, conversions, monotonic ordering, instant arithmetic, SMP coarse-clock saturation, spin waits, and benchmarks for clock reads.
