# sources/user-network-fs/libfuse/lib/fuse_daemonize.c

## Purpose

`fuse_daemonize.c` implements both the legacy `fuse_daemonize(int foreground)` helper and the newer early-daemonization protocol used when a filesystem wants the parent process to remain alive until mount and FUSE initialization are known to have succeeded. The new path is coordinated through `fuse_daemonize_early_start`, `fuse_daemonize_early_success`, `fuse_daemonize_early_fail`, and internal state setters called from mount and FUSE_INIT handling.

The file exists to make daemon startup observable and failure-aware: the original process forks, the parent waits on a pipe, and the child signals success only after the mount has completed and the session has received or processed initialization.

## Important APIs, Types, And Functions

The private `struct fuse_daemonize` stores the requested flags, pipe file descriptors, watcher thread handle, and atomic state bits: `active`, `daemonized`, `mounted`, and `got_init`. The singleton `daemonize` object is file-global and initialized with invalid file descriptors.

New API functions are `fuse_daemonize_early_start(unsigned int flags)`, `fuse_daemonize_early_success(void)`, `fuse_daemonize_early_fail(int err)`, `fuse_daemonize_early_is_used(void)`, `fuse_daemonize_early_is_active(void)`, `fuse_daemonize_early_set_mounted(void)`, and `fuse_daemonize_set_got_init(void)`. The last two are internal coordination hooks declared in `fuse_daemonize_i.h`.

Important private helpers are `do_daemonize`, `daemonize_child`, `parent_watcher_thread`, `start_parent_watcher`, `stop_parent_watcher`, `fuse_daemonize_early_signal`, and `close_if_valid`.

## Control Flow

`fuse_daemonize_early_start` resets the singleton file descriptors, records flags, optionally `chdir("/")`, and if `FUSE_DAEMONIZE_NO_BACKGROUND` is not set marks daemonization active and calls `do_daemonize`. A second call while active returns success without forking again.

`do_daemonize` creates a signal pipe and a death pipe, then forks. The child closes the parent-side pipe ends, records the signal write end and death read end, and calls `daemonize_child`. The parent closes the child-side pipe ends, blocks reading an integer status from the signal pipe, closes both remaining fds, and exits with the received status or failure if the read is short.

`daemonize_child` creates a stop pipe, calls `setsid`, redirects stdin to `/dev/null`, and starts `parent_watcher_thread`. The watcher polls the parent death pipe and stop pipe. If the parent dies before normal completion, the child exits with failure; if the stop pipe is written, it returns normally. Once the watcher is running, the child marks itself daemonized and continues setup.

`fuse_daemonize_early_success` is intentionally tolerant if the new API was not used. When active, it delegates to `fuse_daemonize_early_signal(FUSE_DAEMONIZE_SUCCESS)`. That signal helper suppresses success notification until both `mounted` and `got_init` are true, then deactivates the state, stops the watcher, writes the status to the parent, redirects stdout and stderr to `/dev/null` after successful daemonization, and closes all tracked fds. `fuse_daemonize_early_fail` always attempts to signal an error status through the same path.

The legacy `fuse_daemonize` rejects use after the newer API is active or daemonized. For background mode, it creates a waiter pipe, forks, lets the parent wait for one byte from the child, calls `setsid`, `chdir("/")`, redirects stdin/stdout/stderr to `/dev/null`, signals the parent, and returns in the child. For foreground mode it only changes directory to `/`.

## State And Persistence Behavior

All daemonization state is process-local in the singleton `daemonize`. There is no file persistence. The code mutates process-level state: forks, creates a new session, changes working directory, redirects standard file descriptors, creates pipes, and starts or joins a pthread. Parent and child have independent copies of the singleton after fork, with the child retaining the operational file descriptors.

The `mounted` and `got_init` flags decouple mount completion from FUSE_INIT completion. This is important because libfuse can run synchronous or asynchronous initialization paths; success should be reported only when both conditions needed by the selected mode have occurred.

## Dependencies And Integration Points

This file includes public `fuse_daemonize.h` and internal `fuse_daemonize_i.h`. Its internal setters are expected to be called from mount/session code: `fuse_daemonize_early_set_mounted` from `fuse_session_mount()` and `fuse_daemonize_set_got_init` when FUSE_INIT is handled. Higher-level helper code calls `fuse_daemonize_early_start` before mounting and calls success/failure at appropriate post-mount or init points.

System dependencies include `fork`, `pipe`, `setsid`, `chdir`, `open`, `dup2`, `close`, `read`, `write`, `poll`, `_exit`, pthread creation/joining, atomics, and `errno`/`err` reporting.

## Risks And Edge Cases

The parent exits using the integer status written by the child. `fuse_daemonize_early_fail(int err)` writes the caller's value directly; if callers pass negative errno values, process exit status truncation may be surprising. `FUSE_DAEMONIZE_FAILURE` is defined but not directly used by the fail path.

`parent_watcher_thread` loops on `poll` errors without checking for cancellation or persistent invalid fds. If stop signaling fails, `stop_parent_watcher` still joins and could block if the watcher cannot observe the stop pipe. The new path uses atomics for state bits but not a broader mutex around fd lifecycle; repeated or cross-thread success/failure calls could race around `active` and fd closure.

`fuse_daemonize_early_signal` calls `errx(EINVAL, ...)` if the signal helper is reached while inactive. That exits the process rather than returning an error, so misuse is fatal. Legacy `fuse_daemonize` calls `perror` with a string that already contains a newline and may not have a meaningful `errno` for the "new API already used" case.

## Test Signals

Tests should cover early daemonization in foreground/no-background and background modes, including parent exit status on success and failure, deferral of success until both mounted and got_init are set, parent-death detection before success, stop-watcher cleanup, fd closure, and stdout/stderr redirection after success. Regression tests should verify that legacy `fuse_daemonize` refuses to run after the new API is active and preserves the long-standing foreground/background behavior.
