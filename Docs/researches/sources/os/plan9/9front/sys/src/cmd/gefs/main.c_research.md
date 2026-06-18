# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/main.c

gefs process entry point, runtime initialization, error stack, tracing, and worker startup.

Key responsibilities:
- Parses command-line modes for ream, grow, check-only, readonly, stdio, auth-disable, debug, cache size, trace size, fuzzing, service name, and network announces.
- Allocates global `Gefs`, block cache, deferred-free pool, deadlist cache, trace ring, and per-process error context.
- Installs formatters and starts console, mutator, sweeper, task, reader, sync, network, srv, stdio, and fuzz workers.
- Implements Plan 9-style `waserror()`/`error()`/`broke()`/`nexterror()` over per-process `jmp_buf` stacks.
- Posts `/srv/gefs` and `/srv/gefs.cmd` pipe endpoints.

Important behavior:
- Default cache size is 25% of detected memory from `/dev/swap`.
- Worker processes are `rfork(RFPROC|RFMEM|RFNOWAIT)` children sharing memory.
- `broke()` marks the filesystem readonly before raising the error.
- `writetrace()` and `_babort()` dump trace-ring entries for debugging.

Notable risks:
- `Maxprocs`, epoch slot count, and worker ids must remain coordinated.
- The process exits immediately after launching server workers; service lifetime is in children.
