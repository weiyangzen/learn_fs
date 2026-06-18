# sources/test-tools/stress-ng/stress-exec.c

Purpose: implements `exec`, stressing process creation plus `execve`, `execveat`, and `fexecve` paths against the current stress-ng executable, including optional pthread-originated execs and intentionally invalid executable payloads.

Important APIs/types/functions: `stress_exec_context_t` carries executable paths, large argv/env string, argv/env arrays, O_PATH fd, method selectors, and pthread control. `stress_pid_hash_t` and the hash/free-list helpers track live children and clone stacks. `stress_call_exec_method()`, `stress_do_exec()`, `stress_exec_child()`, `stress_exec_wait()`, and `stress_exec()` implement execution, error classification, reaping, and metrics.

Control flow: `stress_exec()` refuses to run as root, resolves `/proc/self/exe`, allocates PID hash/cache storage and optional huge argument buffer, creates a temp directory for garbage executables, opens the executable with `O_PATH` when needed, and sync-starts. Each iteration spawns up to `exec-max` children using fork, vfork, clone, posix_spawn, or rfork as available. Children redirect stdio, drop capabilities, choose an exec method, sometimes build a garbage executable, sometimes pass huge argv/env data, and either successfully exec `--exec-exit` or return an expected error. The parent continuously reaps children and records failures for optional verification.

State and persistence behavior: runtime state is PID hash tables, clone stacks, child contexts, temp garbage executable paths, optional large mmap strings, and `LD_LIBRARY_PATH` copy. Temporary files are unlinked on cleanup; successful execs replace child process images and leave no durable state.

Dependencies and integration points: uses stress-ng capability, temp-dir, process self-exe, environment, mmap, pthread, scheduler, fork/clone/vfork/spawn/rfork feature gates, and process-state helpers. It registers options for exec method, fork method, max workers, and pthread suppression.

Risks: high `exec-max` can exhaust PIDs, fds, memory, or process limits. `vfork` is intentionally restricted to simple exec paths. Error classification must distinguish expected resource/argument/garbage-exec failures from real regressions. Running as root is blocked because execing arbitrary paths as root would be unsafe.

Test signals: run as non-root with each available `--exec-method` and `--exec-fork-method`, small `--exec-max`, `--exec-no-pthread`, and `--verify`; check no live children remain, temp garbage files are removed, and expected `E2BIG`/`ENOEXEC` paths do not count as verification failures.
