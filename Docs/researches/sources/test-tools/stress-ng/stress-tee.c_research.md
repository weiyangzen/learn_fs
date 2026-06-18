# sources/test-tools/stress-ng/stress-tee.c

## Purpose
Implements the `tee` stressor, which exercises Linux `tee()` by duplicating data between pipes without consuming the input pipe, then drains the original input through `splice()` into `/dev/null`. It validates basic pipe payload ordering while probing error paths such as invalid flags, self-tee, zero-length tee, pipe breakage, and memory pressure.

## Important APIs, Types, And Functions
`stress_tee_t` is the fixed pipe payload containing a length field and monotonically increasing counter. `stress_tee_spawn()` creates a pipe and forks a helper process around a supplied pipe function. `stress_tee_pipe_write()` continuously writes `stress_tee_t` records into the input pipe. `stress_tee_pipe_read()` reads full records from the output pipe and verifies `length` and `counter`. `exercise_tee()` issues focused `tee()` probes for invalid flags on kernels new enough to validate them, same-fd input/output, and zero length. `stress_tee()` orchestrates the helper processes and throughput metric.

## Control Flow
The main stressor installs a `SIGPIPE` stop handler, opens `/dev/null`, waits at the stress-ng sync barrier, spawns the writer helper for `pipe_in`, and spawns the reader helper for `pipe_out`. The parent closes unused pipe ends and loops while the stressor should continue. Most iterations call `tee(pipe_in[0], pipe_out[1], INT_MAX, 0)` without timing; every thousandth iteration measures duration and bytes for the MB/sec metric. Positive tee lengths are drained from `pipe_in[0]` to `/dev/null` with `splice(..., SPLICE_F_MOVE)` so the writer can continue. Each iteration then calls `exercise_tee()` and increments bogo ops.

## State And Persistence Behavior
All state is transient: two helper children, two pipes, `/dev/null`, and the static payloads in each process. There are no persistent files. Cleanup closes the parent pipe ends and kills/reaps both helpers. The helper writer and reader rely on the global stress continue flag and pipe errors to exit.

## Dependencies And Integration Points
The implemented path requires `tee()` and `SPLICE_F_NONBLOCK`; otherwise `stress_unimplemented` is exported. It uses stress-ng fork retry, kill/wait, scheduler, parent-death alarm, signal, metrics, and proc-state helpers. The stressor is classified as `CLASS_PIPE_IO | CLASS_OS | CLASS_SCHEDULER` with `VERIFY_ALWAYS`.

## Risks And Test Signals
Pipe reads can return partial records, so the reader accumulates bytes until a full `stress_tee_t` is available. `EPIPE`, `EAGAIN`, and `EINTR` are expected in pipe-heavy shutdown paths, while other read/write/splice failures are reported. Kernel flag validation differs before Linux 4.10, so invalid-flag checking is version gated. Test signals include sustained bogo progress, verified reader counters, the "MB per sec tee rate" metric, correct handling of helper termination, and unimplemented registration when `tee()` is unavailable.
