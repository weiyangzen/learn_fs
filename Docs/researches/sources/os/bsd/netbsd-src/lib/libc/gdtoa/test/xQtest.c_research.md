# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/xQtest.c

Small generator used by the makefile to choose expected gdtoa test output files.

Behavior:
- Switches on `sizeof(long double)`.
- For 16-byte long double, distinguishes true quad from padded/extended forms by computing `1/3` and checking first/last words.
- Prints shell `cp` commands selecting `x.out`, `xL.out`, `Q.out`, and `pftest.out`.

Purpose: adapt tests to platform long-double representation without hardcoding in the makefile.
