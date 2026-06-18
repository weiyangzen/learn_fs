# sources/test-tools/cthon04/basic/test9.c

Purpose: filesystem-statistics syscall test for the mounted test directory.

Important APIs/types/functions: parses -h, -t, -f, -n plus count. Uses statvfs() on SVR4, statfs() otherwise, including SVR3 signature handling; subr.c supplies statfs on DOS/Win32.

Control flow: enters or reuses the test directory, then loops count times calling the platform filesystem-stat API on '.'.

State and persistence: read-only after optional test-directory creation.

Dependencies and integration points: header selection varies across SVR4, OSF1/BSD, generic sys/vfs, and DOS/Win32 compatibility.

Risks: only checks syscall success, not field correctness; platform-specific statfs structures make portability fragile.

Test signals: success is the count line for statfs/statvfs followed by complete(); any syscall failure exits nonzero.
