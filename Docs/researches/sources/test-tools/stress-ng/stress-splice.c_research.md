# sources/test-tools/stress-ng/stress-splice.c

## Purpose

`stress-splice.c` implements `splice`, a Linux pipe-I/O stressor that moves data through pipes and `/dev/null` using `splice()`. It also exercises pipe-size tuning, splice flags, zero-length and invalid-flag calls, invalid offset combinations, and a looped pipe-to-pipe splice path.

## Important APIs, Types, and Functions

- `stress_splice_flag()` randomly combines available `SPLICE_F_MOVE` and `SPLICE_F_MORE` flags.
- `stress_splice_pipe_size()` uses `F_SETPIPE_SZ` to set pipe capacity to a random multiple of the fixed buffer length.
- `stress_splice_write()` is a fallback writer used when the kernel does not support splicing from `/dev/zero` to a pipe.
- `stress_splice_non_block_write_4K()` primes a pipe for looped splice tests using a temporary nonblocking write.
- `stress_splice_looped_pipe()` splices from one pipe to another and back, disabling the loop path after the first failure.
- `stress_splice()` allocates a fallback buffer, opens `/dev/zero` and `/dev/null`, creates four pipes, configures pipe sizes, runs the splice pipeline, records throughput metrics, and closes/unmaps everything.

## Control Flow

The entry point resolves `splice-bytes`, scaling the configured total across worker instances and enforcing a minimum. It allocates an anonymous fallback buffer, opens `/dev/zero`, creates four pipes, opens `/dev/null`, optionally resizes all pipe ends, primes the looped-pipe path, and enters the synchronized run state.

Each iteration tries to splice `splice_bytes` from `/dev/zero` into pipe 1. If the kernel returns `EINVAL`, the stressor logs once and switches permanently to writing the fallback buffer into the pipe. It then splices pipe 1 to pipe 2 and pipe 2 to `/dev/null`, sampling only every thousandth iteration for lower overhead metrics. It deliberately invokes splice calls expected to fail with `ESPIPE` or invalid flags, performs a zero-size no-op splice, attempts self-splicing, runs the looped pipe path twice, and increments bogo operations. Cleanup follows labeled close paths for every fd and reports "MB per sec splice rate".

## State and Persistence Behavior

Runtime state consists of transient fds for `/dev/zero`, `/dev/null`, and pipes, plus one anonymous fallback buffer. Pipe capacity changes apply only to these fds. No persistent files are created.

## Dependencies and Integration Points

The file depends on `splice()` support and stress-ng mmap, madvise, memory sizing, metrics, and option parsing helpers. It uses `fcntl(F_SETPIPE_SZ)` when available and registers as `CLASS_PIPE_IO | CLASS_OS`. Without `splice()` it exports `stress_unimplemented`.

## Risks and Edge Cases

Linux kernel behavior changed so splicing from `/dev/zero` may be invalid; the fallback write path explicitly handles that. Pipe-size changes may fail because of limits and are ignored. Metrics sample a subset of iterations, so rates are approximate. The multiple cleanup labels set the process state to deinit repeatedly, which is harmless but noisy structurally. Some intentionally invalid splice calls may return different errors across kernels and are ignored.

## Test Signals

Expected signals include successful default runs, fallback log on kernels that reject `/dev/zero` splice, MB/sec splice metric, and no fd leaks. Option coverage should include minimum and large `--splice-bytes` values and builds without `splice()`.
