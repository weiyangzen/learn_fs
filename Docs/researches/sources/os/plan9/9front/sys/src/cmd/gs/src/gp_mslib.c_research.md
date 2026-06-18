# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_mslib.c

Windows graphics-library-specific polling stub.

Key behavior:
- When `CHECK_INTERRUPTS` is enabled, defines `gp_check_interrupts` to return `0`.

Research notes:
- This differs from interpreter polling: the graphics library variant intentionally performs no callback polling here.
