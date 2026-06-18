# File Research: sources/os/bsd/openbsd-src/sys/kern/exec_script.c

Interpreter-script exec handler.

Key behavior:
- Detects `#!` scripts and prevents recursive script processing with `EXEC_INDIR`.
- Requires interpreter line termination within `MAXINTERP`.
- Parses interpreter path and optional single argument.
- Preserves script setuid/setgid metadata for later application.
- If the script is unreadable or set-id, opens it as an fd and passes `/dev/fd/N` to the interpreter.
- Rewrites `nameidata` to point at the interpreter and calls `check_exec()` recursively.
- Builds fake argv: interpreter name, optional interpreter arg, script path or `/dev/fd/N`.
- On success, closes or retains the script vnode as appropriate, frees old namei buffer, sets `EXEC_HASARGL | EXEC_SKIPARG`, and updates credentials metadata.
- On failure, releases fd/vnode, path buffers, fake argv, and vmcmds.

Filesystem/OS relevance:
- Important vnode/namei/file-descriptor interaction during `execve`.
- Shows how OpenBSD handles unreadable and set-id scripts safely through `/dev/fd`.
