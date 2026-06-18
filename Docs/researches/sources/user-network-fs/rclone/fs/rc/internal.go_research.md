# Research: sources/user-network-fs/rclone/fs/rc/internal.go

## sources/user-network-fs/rclone/fs/rc/internal.go

Purpose: registers core/internal rc endpoints: noop, error, panic/fatal test calls, command listing, pid, memory stats, GC, version, obscure, quit, runtime debug knobs, raw `core/command`, and local disk discovery. Key functions include `rcNoop`, `rcError`, `rcPanic`, `rcFatal`, `rcList`, `rcPid`, `rcMemStats`, `rcGc`, `rcVersion`, `rcObscure`, `rcQuit`, debug setters, `rcRunCommand`, `mountOK`, and `rcDisks`.

Control flow is mostly direct parameter parsing and response construction. `rcQuit` exits asynchronously after running atexit hooks. `rcRunCommand` reconstructs command-line args from `command`, `arg`, and `opt`, executes the current binary, and either returns combined output or streams stdout/stderr to an HTTP response. State includes process runtime settings, memory stats, exit scheduling, and external subprocess execution; no durable files are written by this file. Dependencies include buildinfo, obscure, xdg dirs, runtime/debug, os/exec, and rc HTTP response hooks. Risks include exposing command execution, process termination, global runtime knob mutation, response object requirements for streaming, and platform-specific disk filtering. Tests cover most endpoints.
