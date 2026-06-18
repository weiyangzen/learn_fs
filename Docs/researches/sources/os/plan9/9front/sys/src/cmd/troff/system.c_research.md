# File Research: sources/os/plan9/9front/sys/src/cmd/troff/system.c

This file provides a Plan 9 implementation of `system(char *s)` for troff code that expects a Unix-like `system()` helper.

It forks, runs `/bin/rc -c <command>` in the child, waits for the matching child PID, and returns `0` on empty wait message, `1` on non-empty wait status, and `-1` on fork or wait failure.

The implementation is intentionally small and Plan 9-specific. It ignores waits for unrelated children until the target process exits.
