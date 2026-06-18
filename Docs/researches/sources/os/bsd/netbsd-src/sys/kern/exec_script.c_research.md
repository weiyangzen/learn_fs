# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_script.c

## Purpose
Implements `#!` script execution support by transforming a script exec into an interpreter exec with synthetic arguments.

## Main Interfaces
- `exec_script_execsw` registers script recognition using `SCRIPT_HDR_SIZE`.
- `exec_script_modcmd()` adds/removes the script exec handler and refuses autounload to avoid repeated transient unload/reload.
- `exec_script_makecmds()` parses the shebang line, extracts interpreter and optional single interpreter argument, creates fake argv entries, recursively invokes `check_exec()` on the interpreter, and arranges script path or `/dev/fd/N` delivery.

## Dependencies
Uses exec switch infrastructure, pathbuf/namei helpers, file descriptor allocation, vnode access/close operations, optional `FDSCRIPTS`, optional `SETUIDSCRIPTS`, and generic stack setup.

## Implementation Notes
The parser rejects recursive script handling via `EXEC_INDIR`, requires a newline within the script header buffer, strips whitespace before the interpreter, and preserves the historical behavior that all text after the interpreter path is passed as one argument. With `FDSCRIPTS`, unreadable or set-id scripts are passed to the interpreter via `/dev/fd/N`.

## Research Notes
Important invariants are vnode ownership, fd cleanup, fake-argument freeing, and set-id metadata preservation. Error paths close either the temporary fd or original script vnode and destroy VM commands built during a failed interpreter exec.
