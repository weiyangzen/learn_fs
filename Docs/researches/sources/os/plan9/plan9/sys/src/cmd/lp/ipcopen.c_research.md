# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/ipcopen.c

Read fully: 92 lines, 1607 bytes. SHA-256 prefix: `f2c732abf91a86bb`.

This command dials a Plan 9 network endpoint built as `network!destination!service`, opens its data file for reading and writing, then forks bidirectional byte copying between local stdin/stdout and the remote connection.

`pass()` copies until EOF or an initial single NUL byte. The child copies remote-to-stdout, then hangs up. The parent copies stdin-to-remote, then hangs up.

Dependencies: Plan 9 `dial()`, network device directory paths, `hangup()`.

Risk notes: minimal error handling and no protocol framing beyond raw byte pass-through. Some local variables in `pass()` are unused shadows.
