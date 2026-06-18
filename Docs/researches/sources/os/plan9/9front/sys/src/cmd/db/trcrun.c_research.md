# File Research: sources/os/plan9/9front/sys/src/cmd/db/trcrun.c

Purpose: Low-level Plan 9 `/proc` control for `db`.

Key behavior:
- `setpcs()` opens `/proc/<pid>/ctl` and `/proc/<pid>/note` for the current pid.
- `msgpcs()` writes control messages, ending process state on non-interrupt failures.
- `unloadnote()` reads pending notes, discarding breakpoint notes.
- `loadnote()` re-sends saved notes.
- `notes()` prints pending notes.
- `killpcs()`, `grab()`, and `ungrab()` send `kill`, `stop`, and `start`.
- `doexec()` parses run command arguments and `<`/`>` redirection, then execs `symfil`.
- `startpcs()` forks the target, hangs it, execs, maps `/proc/<pid>/mem`, waits for stop, and optionally sets pc.
- `runstep()` computes follow addresses with `machdata->foll()`, plants temporary breakpoints, runs, then removes them.
- `runrun()` starts/stops the process, preserving or discarding notes as requested.
- `bkput()` installs/restores machine-specific breakpoint instruction bytes.

Notable details:
- Single-step is implemented with temporary breakpoints at possible next instruction addresses, not hardware stepping.
- `bkput()` applies optional `machdata->bpfix()` to adjust breakpoint address.
