# File Research: sources/os/plan9/9front/sys/src/cmd/rc/fns.h

Shared prototype header for `rc`. It centralizes platform abstraction calls, allocator helpers, parser/compiler hooks, glob/match helpers, I/O formatting helpers, variable/environment initialization, trap dispatch, and command execution helpers.

Key abstraction boundary: generic shell code calls exported names such as `Open`, `Creat`, `Fork`, `Waitfor`, `Opendir`, `Readdir`, `Errstr`, and `Exec`; `plan9.c` and `unix.c` provide platform-specific implementations.

This file documents the shell’s internal module graph without implementation details.
