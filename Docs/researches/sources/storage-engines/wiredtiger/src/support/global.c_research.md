# sources/storage-engines/wiredtiger/src/support/global.c

## Purpose
`global.c` owns process-wide WiredTiger initialization. It defines the global `WT_PROCESS __wt_process`, the timing stress name-to-flag table `__wt_stress_types`, validates runtime endianness against build configuration, initializes process locks and connection queues, installs checksum entry points, and calibrates the clock path used by `__wt_clock`.

## Important APIs, Types, and Functions
The exported entry point is `__wt_library_init`, which must run before most library work. It calls `__endian_check`, then `__wt_once(__global_once)` behind a local `first` guard and returns any cached initialization failure through `__wt_pthread_once_failed`. `__global_once` initializes `__wt_process.spinlock`, `__wt_process.connqh`, checksum functions from `wiredtiger_crc32c_func` and `wiredtiger_crc32c_with_seed_func`, and clock configuration through `__global_setup_clock`.

On `__amd64` and `__aarch64__`, the file also contains TSC calibration helpers: `__reset_thread_tick`, `__get_epoch_and_tsc`, `__compare_uint64`, `__get_epoch_call_ticks`, `__get_epoch_and_ticks`, and `__global_calibrate_ticks`. These compute a `tsc_nsec_ratio` by measuring `__wt_epoch` latency and comparing elapsed wall-clock nanoseconds to `__wt_rdtsc` ticks across a short sleep.

## Control Flow
Initialization begins with a hard compatibility check: a build compiled for the wrong endian mode returns `EINVAL` and emits a stderr diagnostic. The one-time global initializer sets up synchronization and queues, then defaults clocking to `__wt_epoch`. On supported CPU families, calibration tries to obtain low-jitter wall-clock/TSC pairs, sleeps for `CLOCK_CALIBRATE_USEC`, and only switches `__wt_process.use_epochtime` to `false` if the measured ratio is meaningful.

## State and Persistence Behavior
All state is in process memory. `__wt_process` persists for the life of the process and stores lock state, the connection queue, checksum callbacks, clock calibration fields, and standalone-build flags. `__wt_pthread_once_failed` persists the first initialization failure. No disk state is written.

## Dependencies and Integration Points
This file depends on WiredTiger internal primitives from `wt_internal.h`: `__wt_once`, spin locks, `TAILQ_INIT`, CRC32C selector functions, clock helpers, TSC reads, sleeps, qsort, and timing macros. It integrates with connection open paths that call `__wt_library_init`, runtime timing-stress configuration via `__wt_stress_types`, and any code using `__wt_clock`.

## Risks
Clock calibration is intentionally best-effort; noisy scheduling, low timer granularity, virtualized TSC behavior, or unstable CPU counters can leave the engine on the epoch-time fallback. The qsort comparator casts a `uint64_t` difference to `int`, which is acceptable for relative ordering in this local calibration set only if differences remain small enough not to produce misleading comparator results. The local `first` optimization is fronting a true once primitive, so correctness depends on `__wt_once` for race safety, while the local flag only reduces overhead.

## Test Signals
Useful tests include startup on big- and little-endian builds, repeated concurrent calls to `__wt_library_init`, injected spin-lock initialization failure, deterministic mapping of every `__wt_stress_types` name to a unique flag, and clock behavior on TSC-capable and non-TSC platforms. Runtime stats or targeted tests should verify that `use_epochtime` remains true when calibration fails and flips only after a valid ratio is measured.
