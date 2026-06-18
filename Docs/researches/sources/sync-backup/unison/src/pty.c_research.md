# sources/sync-backup/unison/src/pty.c

Purpose: OCaml C stubs for pseudo-terminal and controlling-terminal support on Unix-like systems and Windows.

Important APIs: Unix `setControllingTerminal` and `c_openpty`; Windows `win_openpty`, `win_closepty`, `w_create_process_pty`, and `win_alloc_console`; non-supported fallbacks raise `ENOSYS`.

Control flow: Unix variants use `openpty` and `ioctl(TIOCSCTTY)`, with Cygwin calling `setsid` because OCaml lacks it there. Windows dynamically resolves `CreatePseudoConsole`/`ClosePseudoConsole`, creates separate pipes for ConPTY input/output, returns OCaml handles plus an abstract HPCON, builds `STARTUPINFOEX` with pseudo-console and handle-list attributes, duplicates std handles, launches a child with `CreateProcessW`, cleans duplicated handles/attribute lists, and returns the process handle.

State/persistence: creates OS PTY handles, pipes, consoles, child processes, and process handles. `win_alloc_console` may attach a console and repair C runtime `stderr`.

Dependencies/integration: Unix libutil/pty headers, Windows ConPTY APIs, OCaml handle allocation, and SSH/terminal interaction code.

Risks: Windows ConPTY is available only on newer systems, so dynamic ENOSYS paths are important. Handle inheritance and cleanup are subtle. `hStdError` is intentionally NULL for Cygwin/MSYS2 SSH compatibility. Abstract HPCON lacks a finalizer, so OCaml must close it correctly.

Test signals: interactive SSH/password prompt behavior, PTY open/close, child process launch, console fallback, Cygwin/MSYS2 clients, and handle leak checks.
