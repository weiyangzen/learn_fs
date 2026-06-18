# sources/test-tools/stress-ng/stress-hdd.c

## Purpose
`stress-hdd.c` is a filesystem I/O stressor that creates a temporary file per worker, writes and reads it sequentially or randomly, optionally uses sync/direct/iovec/fadvise modes, verifies data patterns, and reports read/write throughput and extent counts.

## Important APIs, Types, And Functions
Options include `hdd-bytes`, `hdd-write-size`, `hdd-opts`, and `hdd-sleep`. `stress_hdd_opts_t` maps option strings to internal flags, exclusions, fadvise advice, and open flags. `stress_hdd_opts()` parses comma-separated modes and stores derived settings. `stress_hdd_write()` and `stress_hdd_read()` choose among `write`, `writev`, `pwritev`, `pwritev2`, `read`, `readv`, `preadv`, and `preadv2`. `stress_hdd_invalid_read()` and `stress_hdd_invalid_write()` exercise negative syscall paths. `data_value()` and `hdd_fill_buf()` produce deterministic verification data.

## Control Flow
`stress_hdd()` clamps sizes, derives per-instance file size, creates a temp directory and aligned buffer, waits at the barrier, then repeatedly opens/truncates/unlinks a temp file, applies fadvise, runs invalid I/O coverage, performs selected random/sequential writes, stats the file, performs selected reads with optional verification, records extent counts, closes the fd, and optionally sleeps. Aggressive mode cycles through individual hdd options when no explicit options are set.

## State And Persistence
The stressor creates temporary directories and files through stress-ng filesystem helpers and removes them before exit. Metrics accumulate read/write byte counts and durations in process memory. It may affect filesystem caches, allocation state, atime/mtime, and sync pressure while running.

## Dependencies And Integration Points
It depends on POSIX file APIs, optional vectored I/O, `posix_fadvise`, sync calls, `futimes`, aligned allocation, stress-ng temp-file helpers, extent probing, metrics, and global minimize/maximize/aggressive/verify flags.

## Risks
This stressor can consume significant disk space and I/O bandwidth. `O_DIRECT` alignment and filesystem support vary. Random writes can leave sparse/zero regions, handled specially by verification. Some filesystems return `ENOSPC`, `EDQUOT`, partial reads, or unsupported direct I/O. Option exclusions must stay consistent to avoid contradictory modes.

## Test Signals
Important signals are successful temp cleanup, correct option parsing/exclusion errors, valid data verification under sequential/random modes, tolerated `ENOSPC` retry behavior, no aligned-buffer faults with `O_DIRECT`/iovec, and populated read/write/combined throughput plus extent metrics.
