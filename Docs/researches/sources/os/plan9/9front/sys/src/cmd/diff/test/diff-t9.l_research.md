# File Research: sources/os/plan9/9front/sys/src/cmd/diff/test/diff-t9.l

Very large C-source diff fixture based on NetBSD `vfs_syscalls.c`.

Key behavior:
- Begins with `/*	$NetBSD: vfs_syscalls.c...`.
- Contains VFS syscall implementations and helper routines, including open/close/read/write/lseek/access/stat/readlink/chmod/chown/rename/mkdir/rmdir/getdirentries/umask/revoke and vnode/file-descriptor handling.
- Ends with a closing brace.

Research notes:
- 2045-line realistic filesystem-heavy C fixture, directly relevant to broad filesystem research even though it lives under diff tests.
- Exercises diff behavior on long source files with many repeated syscall patterns and comments.
