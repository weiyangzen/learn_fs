# sources/test-tools/stress-ng/stress-ring-pipe.c

Purpose: implements `ring-pipe`, a pipe I/O stressor that creates a ring of nonblocking pipes and circulates buffers around the ring using either read/write or `splice()`.

Important APIs/types/functions: `pipe_fds_t` stores each pipe pair. `stress_pipe_non_block()` sets `O_NONBLOCK`. `stress_pipe_read()` and `stress_pipe_write()` wrap I/O with diagnostics. `stress_ring_pipe_info` exposes `ring-pipe-num`, `ring-pipe-size`, and `ring-pipe-splice`, with `VERIFY_NONE`.

Control flow: `stress_ring_pipe()` allocates a max-size buffer, pipe fd table, and pollfd table, creates as many pipes as possible up to the requested count, sets read fds in `poll()`, and falls back from splice if unavailable. After sync it seeds two pipes with data. The main loop polls for readable pipes; each readable pipe sends its data to the next pipe in the ring via `splice()` or read/write, tracking duration, bytes, and bogo operations.

State and persistence: state is process-local memory and kernel pipe fds only. Cleanup closes every created fd, frees arrays, unmaps the buffer, and reports metrics.

Dependencies and integration points: requires `poll.h` and `poll()`. Optional splice mode depends on `HAVE_SPLICE` and `SPLICE_F_MOVE`. It uses stress-ng mmap helpers, settings, sync, metrics, and random/stop helpers.

Risks and test signals: fd limits can reduce the requested pipe count, and nonblocking pipe I/O may encounter transient failures. Metrics report pipe read/write calls per second and MB/s written through pipes. Since verification is disabled, success is mainly absence of unexpected poll timeouts, I/O errors, and fd leaks.
