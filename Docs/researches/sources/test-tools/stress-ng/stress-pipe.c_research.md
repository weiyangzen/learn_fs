# sources/test-tools/stress-ng/stress-pipe.c

Purpose: `stress-pipe.c` implements the `pipe` stressor, creating reader and writer process groups around a pipe to stress pipe throughput, packet mode, pipe sizing, `vmsplice`, signal shutdown, and optional data verification.

Important APIs/types/functions: `stress_pipe_write_t` stores per-writer duration and byte counts in shared memory. `pipe_get_size()` and `pipe_change_size()` read/set pipe buffer size. Read/write helpers cover generic `read`/`write` and optional `vmsplice`, with verified and unverified variants. Option callbacks parse `pipe-size` and `pipe-data-size`.

Control flow: the stressor resolves reader/writer counts, data size, pipe size, and vmsplice option, disables verification when multiple readers or writers make ordering nondeterministic, mmaps writer metrics, installs SIGPIPE stop handling, creates a pipe or `pipe2(O_DIRECT)` packet-mode pipe, sizes the pipe, mmaps read/write buffers, fills write data, synchronizes, and forks readers then writers. Children close unused pipe ends, apply scheduling/affinity, and run the chosen read or write loop. The parent sleeps until stop, sends SIGPIPE to children, waits for them, aggregates writer bytes/durations, and reports MB/s.

State and persistence behavior: state is anonymous shared writer metrics, pipe fds, private read/write buffers inherited by children, and child pid arrays. No files persist. SIGPIPE handling controls orderly shutdown.

Dependencies and integration points: pipe/pipe2, optional `O_DIRECT` packet mode, `F_GETPIPE_SZ`/`F_SETPIPE_SZ`, optional `vmsplice`, `FIONREAD`, stress-ng affinity/scheduler/signal/mmap helpers, and `CLASS_PIPE_IO | CLASS_MEMORY | CLASS_OS | CLASS_IPC` registration with optional verify.

Risks: high process counts can exhaust fork capacity. Verified mode only works for one reader and one writer. In the final wait section, the writer wait loop iterates `i < pipe_readers` while indexing `wr_pids`, so if writer count exceeds reader count some writer children may not be waited there. `vmsplice` is disabled unless packet mode is available.

Test signals: `--pipe` should produce MB/s metrics and clean child exit. Important variants include `--pipe-vmsplice`, explicit pipe sizes, min/max reader/writer counts, verify with a single reader/writer, and low fork/fd resource conditions.
