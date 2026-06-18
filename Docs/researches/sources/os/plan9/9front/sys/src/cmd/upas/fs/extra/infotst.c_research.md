# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/extra/infotst.c

This helper simulates clients reading `info` pseudo-files with varying read sizes.

Key behavior:
- Usage: `infotest n1 n2 ... nm`.
- Reads stdin repeatedly with the provided block sizes, cycling at the last size, and writes exactly what was read to stdout.
- Comments document verification workflows comparing `upas/fs` info file behavior across read patterns and old/new implementations.

Integration and risks:
- Pure test harness for client read pattern sensitivity.
