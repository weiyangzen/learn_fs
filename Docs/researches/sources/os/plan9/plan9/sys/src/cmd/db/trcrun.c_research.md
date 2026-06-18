# File Research: sources/os/plan9/plan9/sys/src/cmd/db/trcrun.c

This file contains Plan 9 `/proc` control operations used to run and trace a debugged process.

Key behaviors:
- Maintains `/proc/<pid>/ctl` and `/proc/<pid>/note` descriptors.
- `setpcs()` opens control and note files for the current `pid`, refreshing when `pid` changes.
- `msgpcs()` writes process-control messages such as `hang`, `waitstop`, `startstop`, `stop`, `start`, and `kill`.
- `unloadnote()` reads pending notes and discards `"sys: breakpoint"` notes.
- `loadnote()` writes saved notes back before continuing.
- `notes()` displays saved notes.
- `grab()` stops a process and waits; `ungrab()` starts it.
- `doexec()` parses arguments and simple `<`/`>` redirections, then `exec()`s `symfil`.
- `startpcs()` forks, hangs the child, execs target program, sets `corfil` to `/proc/<pid>/mem`, waits for stop, and optionally sets the PC.
- `runstep()` implements single stepping using machine-specific follow addresses and temporary breakpoints.
- `bpwait()` refreshes `cormap` and note state after stops.
- `runrun()` starts/stops the process, preserving notes only when requested.
- `bkput()` installs/removes breakpoint instructions in process memory.

Notable implementation details:
- Single-step fallback assumes the next instruction is `loc + mach->pcquant`.
- `bkput()` applies optional machine breakpoint address fixup before patching memory.
- Breakpoint patch failure prompts on stdin after printing an error.
