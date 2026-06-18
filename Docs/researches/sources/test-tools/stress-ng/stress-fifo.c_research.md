# sources/test-tools/stress-ng/stress-fifo.c

Purpose: implements `fifo`, a named-pipe I/O stressor with one writer and multiple reader child processes validating ordered fixed-size records through a FIFO.

Important APIs/types/functions: `fifo_spawn()` forks synchronized reader processes. `stress_fifo_reader()` opens the FIFO nonblocking, waits with `poll()` or `select()`, optionally probes queued bytes with `ioctl(FIONREAD)`, reads exactly `fifo_data_size` bytes, validates monotonic record numbers with wrap masking, and occasionally exercises invalid FIFO operations such as `lseek()` and `mmap()`. `stress_fifo()` creates the FIFO, spawns readers, writes records, and reports write rate.

Control flow: option handling selects `--fifo-readers` and `--fifo-data-size`, applying minimize/maximize defaults. The parent creates a temp directory and FIFO, starts reader children, synchronizes, opens the FIFO for writing, repeatedly writes an aligned buffer whose first `uint64_t` increments, updates metrics and bogo operations, then closes, kills readers, unlinks the FIFO, and removes the temp dir.

State and persistence behavior: creates one temporary FIFO path and a mapped pid table for reader management. Data state is transient in the FIFO and aligned buffers. Cleanup removes the FIFO and temp directory.

Dependencies and integration points: requires `mkfifo()` and `sys/select.h`; uses `poll()` when available. Integrates with stress-ng sync-start pid lists, kill/wait helpers, temp-file helpers, pathconf probes, and metrics. Registered as `CLASS_PIPE_IO | CLASS_OS | CLASS_SCHEDULER | CLASS_IPC`, `VERIFY_ALWAYS`.

Risks: nonblocking readers can observe partial or zero reads during shutdown or overload; code treats wrong-size reads as failure. The order check assumes a single writer and fixed-size records. `fifo_data_size` is capped to 4096, aligning with portable pipe atomicity assumptions.

Test signals: run with reader counts 1 and 64 and data sizes 8 and 4096. Check write-rate metric name includes the byte size, no "did not get buffer" failures occur, and FIFO cleanup succeeds after interrupted runs.
