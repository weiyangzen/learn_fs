# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/unix.h

Read status: complete, 53 lines.

This header configures the Unix build environment for `rc`. It undefines and redefines feature-test macros, includes POSIX/BSD C headers, defines `NSIG` fallback, and declares Plan 9 compatibility constants and types.

It maps Plan 9 open modes to Unix `O_RDONLY`, `O_WRONLY`, and `O_RDWR`, defines `nil`, aliases Plan 9 integer typedef names, and provides no-op or compatibility definitions for `RFPROC`, `RFFDG`, `RFNOTEG`, and `OCEXEC`.

Filesystem relevance: this is the shim that lets code written against Plan 9-style file and process constants compile on Unix.
