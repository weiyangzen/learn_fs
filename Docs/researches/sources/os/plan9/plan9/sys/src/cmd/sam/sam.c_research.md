# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/sam.c

Contains the host `sam` main program, global state, lifecycle, recovery, file loading, and common edit operations.

Key responsibilities:
- `main` parses flags, initializes strings, disk storage, terminal startup, signal notifications, current directory, initial files, and enters `cmdloop`.
- `rescue`, `panic`, and `hiccough` implement crash/error recovery and save dirty buffers to `$home/sam.save`.
- `load`, `edit`, `readcmd`, `readflist`, `getfile`, `tofile`, and `closefiles` implement file input and command file-list behavior.
- `update`, `cmdupdate`, `delete`, `trytoclose`, and `trytoquit` manage file lifecycle and dirty-state safety.
- `copy`, `move`, `undo`, `undostep`, `printposn`, and `settempfile` provide shared editor operations.

Behavior notes:
- Dirty-file quit protection is mediated by `quitok`, `closeok`, and per-file `mod` state.
- File reads and writes use command-level globals `addr`, `genstr`, `genc`, and `io`.
- Recovery emits a shell script using `SAMSAVECMD` to recreate dirty files.

Risk/maintenance notes:
- Error recovery uses `setjmp`/`longjmp` and extensive global state.
- `rescue` skips the command file, empty files, and clean files.
