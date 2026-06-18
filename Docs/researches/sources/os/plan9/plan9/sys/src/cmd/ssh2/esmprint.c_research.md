# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/esmprint.c

This file provides `esmprint`, an allocating formatted-string helper.

Key behavior:
- Wraps `vsmprint`.
- Calls `sysfatal` on allocation failure.
- Sets the malloc tag to the caller pc for debugging/allocation tracking.

Important details:
- Used by SSH utilities to avoid repetitive out-of-memory checks on formatted path/control strings.

Filesystem relevance:
- Indirect: commonly formats Plan 9 namespace paths such as `/net/ssh/...`, `/srv/...`, and `/proc/...`.
