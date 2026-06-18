# File Research: sources/os/plan9/9front/sys/src/cmd/acid/proc.c

This file manages Acid's attachment to Plan 9 processes through `/proc`.

Key responsibilities:
- `nocore()` closes existing core-map segment file descriptors and frees the current `cormap`.
- `sproc(pid)` opens `/proc/<pid>/mem`, validates it against the symbol map, attaches a process memory map, labels text/data segments, sets the Acid `pid` variable, and installs the process in Acid's table.
- `nproc(argv)` forks a new child, hangs it through `/proc/<pid>/ctl`, resets stdio to `/dev/cons`, execs the requested program, then attaches Acid to it.
- `notes(pid)` reads pending process notes from `/proc/<pid>/note` into the Acid `notes` list.
- `dostop(pid)` calls the user-defined `stopped(pid)` Acid hook if present.
- `install()` and `deinstall()` maintain `ptab`, `proclist`, process control fds, and `pid`.
- `msg(pid, msg)` sends control messages to `/proc/<pid>/ctl`.
- `getstatus(pid)` reads and tokenizes `/proc/<pid>/status`.
- `waitfor(pid)` waits specifically for a given process.

Important dependencies:
- Uses Plan 9 `/proc` files: `mem`, `ctl`, `note`, `status`.
- Uses libmach process/core-map functions such as `attachproc`, `findseg`, and `checkqid`.
- Updates Acid variables via `look()`, `al()`, `strnode()`, and `execute()`.

Filesystem/storage relevance:
- Strongly process-filesystem oriented: `/proc` is used as the debugging control and memory interface.
- Shows Plan 9's file-backed process control model in compact form.

Notes:
- `msg()` treats `"process exited"` specially by deinstalling the process before reporting the error.
- New child setup uses `rfork(RFNAMEG|RFNOTEG)` to isolate namespace and notes.
