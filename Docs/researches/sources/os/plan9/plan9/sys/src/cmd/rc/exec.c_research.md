# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/exec.c

Core rc interpreter, word/list stack management, variable handling, and many `X*` opcode implementations.

Startup:
- `main()` parses flags, initializes traps/keywords/environment, sets `$pid`, `$cflag`, `$rcname`, builds bootstrap code to assign `$*` and run rcmain, then enters the dispatch loop.
- `start()` pushes a new `thread` frame with code, pc, local vars, redirection inheritance, command input state, and return link.

Stack/data helpers:
- `newword()`, `pushword()`, `popword()`, `pushlist()`, `poplist()`, `freelist()`, `freewords()`, `count()`.
- `pushredir()` stores pending redirections.
- `newvar()` allocates variable records.

Opcode coverage includes:
- redirection open/close/dup: `Xappend`, `Xread`, `Xrdwr`, `Xwrite`, `Xclose`, `Xdup`, `Xpopredir`;
- status/control flow: `Xsettrue`, `Xbang`, `Xeflag`, `Xexit`, `Xfalse`, `Xtrue`, `Xif`, `Xifnot`, `Xwastrue`, `Xjump`, `Xreturn`;
- stack/list operations: `Xmark`, `Xpopm`, `Xword`, `Xconc`;
- matching: `Xmatch`, `Xcase`;
- variables: `Xassign`, `Xdol`, `Xqdol`, `Xsub`, `Xcount`, `Xlocal`, `Xunlocal`;
- functions: `Xfn`, `Xdelfn`;
- pipes/status: `Xpipewait`;
- command reading: `Xrdcmds`;
- errors/status: `Xerror`, `Xerror1`, `setstatus()`, `getstatus()`, `truestatus()`;
- heredoc cleanup and loops: `Xdelhere`, `Xfor`, `Xglob`.

Risk/notes:
- `Xexit()` runs `sigexit` once in the main shell before exiting.
- Error paths unwind non-interactive threads back to the command loop or exit.
- Word lists are often reversed internally and restored by callers.
