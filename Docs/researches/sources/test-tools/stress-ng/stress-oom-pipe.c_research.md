# sources/test-tools/stress-ng/stress-oom-pipe.c

Purpose: `stress-oom-pipe.c` implements the `oom-pipe` stressor, which deliberately opens many pipes, grows pipe buffers with `F_SETPIPE_SZ`, and fills/drains them to stress kernel pipe memory allocation and OOM handling.

Important APIs/types/functions: the build requires `F_SETPIPE_SZ`, `F_SETFL`, and `O_NONBLOCK`. `stress_oom_pipe_context_t` carries descriptor limits, maximum pipe size, shared read/write buffers, and the descriptor array. `pipe_fill()` writes page-sized chunks with a changing first word; `pipe_empty()` drains page-sized chunks. `stress_oom_pipe_child()` performs the pipe open/grow/fill/shrink loop, and `stress_oom_pipe()` allocates buffers/descriptors and runs the child through `stress_oomable_child()`.

Control flow: the parent mmaps two page buffers, discovers file-descriptor and pipe-size limits, allocates an fd table, waits at the sync barrier, and launches an oomable child. The child drops capabilities, initializes all fds to `-1`, opens as many nonblocking pipes as possible, then repeatedly grows each pipe to the maximum rounded pipe size, fills it, optionally drains it unless aggressive mode is active, exercises invalid pipe sizes, shrinks to one page, fills/drains again, and increments bogo ops.

State and persistence behavior: all state is process-local or anonymous memory: descriptor arrays, two pipe buffers, and kernel pipe buffers. The child closes every opened fd in cleanup. No filesystem artifacts are created.

Dependencies and integration points: it integrates with stress-ng OOM controls, capability dropping, memory-low checks, file-limit helpers, pipe-size helpers, mmap naming, sync barriers, and `CLASS_MEMORY | CLASS_OS | CLASS_PATHOLOGICAL` registration with `VERIFY_ALWAYS`.

Risks: the stressor intentionally consumes pipe memory and file descriptors; on systems without OOM avoidance it can trigger memory pressure. `fcntl(F_SETFL, O_NONBLOCK)` failure aborts through cleanup, but fd pressure before `pipes_open` can return `EXIT_NO_RESOURCE`. Aggressive mode leaves pipe contents queued for more memory pressure.

Test signals: direct `--oom-pipe` runs should show bogo progress and clean descriptor teardown. Useful variants include aggressive mode, OOM-avoid mode, low fd limits, systems with small `/proc/sys/fs/pipe-max-size`, and builds missing the required fcntl constants.
