# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/private.c

Process hardening helper for commands handling keys or passwords.

Key responsibilities:
- Opens `/proc/<pid>/ctl`.
- Writes `private` to prevent debugging by other processes.
- Writes `noswap` to prevent sensitive pages from being swapped.
- Emits warnings if either protection fails.

Dependencies:
- Uses Plan 9 proc control semantics.
