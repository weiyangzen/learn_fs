# sources/test-tools/stress-ng/stress-revio.c

Purpose: implements `revio`, a reverse-I/O filesystem stressor that creates a temporary file, truncates it to a target size, and writes fixed-size blocks from high offsets toward low offsets with optional open, sync, timestamp, readahead, and `posix_fadvise()` modes.

Important APIs/types/functions: `stress_revio_info` exposes `revio-bytes` and callback option `revio-opts`. `stress_revio_opts()` parses comma-separated mode names and rejects incompatible advice combinations. `stress_revio_advise()` applies selected fadvise hints. `stress_revio_write()` performs the write plus optional `futimes()`, `fsync()`, `fdatasync()`, and `syncfs()`.

Control flow: `stress_revio()` reads configured flags, forces `REVIO_OPT_O_DIRECT`, sizes per-instance I/O, creates a temp directory, allocates a 4096-aligned 1024-byte buffer, and synchronizes. Each iteration optionally rotates through modes under aggressive mode, opens and unlinks a temp file, truncates it, applies fadvise, then writes at decreasing offsets using randomized stride gaps. It tracks extent counts and optionally performs `readahead()` after dropping cache advice.

State and persistence: filesystem state is temporary and unlinked early after opening, with the directory removed at the end. State includes the aligned buffer, option flags, iteration counters, and average extent metric.

Dependencies and integration points: depends on stress-ng filesystem temp helpers, file extent helpers, write-hint helper, random buffer generation, settings callbacks, and conditional libc/kernel APIs such as `posix_memalign`, `posix_fadvise`, `readahead`, and sync calls.

Risks and test signals: direct I/O alignment and filesystem support are common failure points; ENOSPC retries are expected. Signals include bogo increments per successful block write, geometric mean extent metric, correct rejection of invalid option strings, and cleanup of temp directories on all exits.
