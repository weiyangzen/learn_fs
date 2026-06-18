
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/pipe.c -->
# Research: sources/sync-backup/rsync/pipe.c

## Purpose
`pipe.c` creates inter-process communication channels for remote-shell children and local rsync child processes. It hides pipe/socketpair setup, fork/exec, descriptor duplication, and local child role adjustments.

## Important APIs, Types, and Functions
- `piped_child(char **command, int *f_in, int *f_out)` forks and execs an external remote-shell command connected to rsync by stdin/stdout pipes.
- `local_child(int argc, char **argv, int *f_in, int *f_out, int (*child_main)(int, char*[]))` forks another in-process rsync role for local transfers and calls `child_main()` in the child.
- Extern state includes `am_sender`, `am_server`, `blocking_io`, `filesfrom_fd`, `munge_symlinks`, `logfile_name`, `remote_options`, and `chmod_modes`.

## Control Flow
Both functions create two fd pairs: parent-to-child and child-to-parent. After `do_fork()`, the child duplicates the read side of the input pair to stdin and the write side of the output pair to stdout, closes unused ends, and then either execs `command[0]` (`piped_child`) or adjusts rsync role state and calls `child_main()` (`local_child`). The parent closes child-only ends and returns the child pid plus read/write descriptors via `f_in` and `f_out`.

## State and Persistence
State changes are process-local after fork. `piped_child()` sets child stdin blocking and optionally stdout blocking based on `blocking_io`. `local_child()` changes the child to server/receiver role, resets `filesfrom_fd`, disables sender-side symlink munging, clears `chmod_modes`, closes client-side logfile state, and parses any `remote_options` before connecting stdio. No durable state is written.

## Dependencies and Integration Points
The file depends on rsync wrappers `fd_pair()`, `do_fork()`, `set_blocking()`, `rsyserr()`, `exit_cleanup()`, logging helpers, `parse_arguments()`, `option_error()`, and optional `setup_iconv()`. It integrates with remote-shell startup, local transfers, and option propagation from `options.c`.

## Risks
IPC setup failures abort the process. Descriptor leaks or wrong close order would deadlock rsync. `local_child()` must keep role-specific global resets aligned with option semantics; missing a reset could make the local receiver inherit sender-only behavior. `remote_options` parsing in the child can fail after fork and must report cleanly. External `execvp()` depends on `PATH`.

## Test Signals
Exercise remote-shell command execution, failed `pipe`/`fork`/`exec` paths, blocking and nonblocking modes, local transfer child role flags, remote option parsing failures, logfile closure, iconv setup, and descriptor liveness/deadlock under large transfers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/pipe.c -->
