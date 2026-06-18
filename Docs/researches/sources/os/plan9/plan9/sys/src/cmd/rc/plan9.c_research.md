# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/plan9.c

Plan 9 platform adapter for rc.

Major responsibilities:
- Defines signal names, rcmain path, fd prefix, and builtin table.
- Builtin `rfork` implementation in `execnewpgrp()`.
- `Vinit()` imports `/env` variables into rc variables.
- `Xrdfn()` and `execfinit()` read function definitions from `/env/fn#*`.
- `Waitfor()` wraps Plan 9 wait, integrates with tracked child pids and pipeline status.
- `mkargv()`, `addenv()`, `Updenv()` convert rc variables/functions back to `/env`.
- `ForkExecute()` and `Execute()` start external programs with path search and env update.
- Directory/glob adapter: `Globsize()`, `Opendir()`, `Readdir()`, `Closedir()`.
- Trap adapter: `notifyf()`, `Trapinit()`, `Eintr()`, `Noerror()`.
- System wrappers: `Unlink`, `Read`, `Write`, `Seek`, `Executable`, `Creat`, `Dup`, `Exit`, `Isatty`, `Abort`, `Malloc`.
- Wait-pid tracking: `addwaitpid()`, `delwaitpid()`, `clearwaitpids()`, `havewaitpid()`.

Risk/notes:
- Environment synchronization is explicit and change-flag based.
- `Exit()` writes environment before exiting.
- `notifyf()` converts Plan 9 notes into rc trap counters and avoids infinite trap loops.
