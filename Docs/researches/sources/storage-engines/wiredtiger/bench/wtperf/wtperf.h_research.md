# sources/storage-engines/wiredtiger/bench/wtperf/wtperf.h

## Purpose
`wtperf.h` is the shared contract for the wtperf benchmark. It defines extension paths, workload operation codes, benchmark state structs, time conversion macros, tracking structures, exported helper prototypes, and key encode/decode helpers used across the wtperf C files.

## Important APIs, Types, And Functions
Important types are `WORKLOAD`, `TRUNCATE_CONFIG`, `TRUNCATE_QUEUE_ENTRY`, `THROTTLE_CONFIG`, `WTPERF`, `TRACK`, and `WTPERF_THREAD`. `WTPERF` owns connection-level state, URIs, config, thread arrays, counters, volatile lifecycle flags, and truncate queue head. `WTPERF_THREAD` owns per-thread buffers, RNG state, throttle/truncate config, random cursor, and per-operation `TRACK` counters. Inline helpers include `generate_key`, `extract_key`, and `die`.

## Control Flow
The header does not execute logic directly, but it shapes all call boundaries: `wtperf.c` drives lifecycle, `wtperf_config.c` fills `CONFIG_OPTS` and workload arrays, `wtperf_misc.c` logs/backs up/indexes, `wtperf_throttle.c` consumes `THROTTLE_CONFIG`, and `wtperf_truncate.c` consumes the truncate queue/config.

## State And Persistence Behavior
State here is purely structural. Persistent effects are mediated by fields such as `home`, `monitor_dir`, table URIs, and connection/table configuration strings. The header documents intentionally shared counters and volatile flags but does not provide synchronization beyond callers' use of atomics for selected counters.

## Dependencies And Integration Points
The header includes `test_util.h`, `<math.h>`, and `config_opt.h`, and exposes WiredTiger API types such as `WT_CONNECTION`, `WT_SESSION`, and `WT_CURSOR`. Compression and tiered extension constants integrate command-line options with dynamic extension loading or built-in extension builds.

## Risks
The biggest risk is that this header is a broad shared mutable contract. Changes to struct layout or option-derived buffer sizing affect multiple files and thread paths. `volatile bool` flags are lifecycle hints, not full synchronization primitives. Buffer sizes rely on `key_sz` and `value_sz_max` being validated before thread startup.

## Test Signals
Compile coverage across all wtperf C files is the primary signal. Runtime tests should exercise all declared helpers: backup, config parsing, latency aggregation, truncate, throttling, index-like table operations, and idle table cycling.
