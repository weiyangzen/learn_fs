<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/avcstat.c -->
# sources/security-integrity/selinux/libselinux/utils/avcstat.c

## Purpose
Displays SELinux AVC cache statistics from selinuxfs, either once or at an interval.

## Important APIs, Types, And Functions
`main()` parses `-c`, `-f`, and optional interval. `set_window_rows()` sizes header repetition from terminal rows. `die()` reports fatal parse/read errors.

## Control Flow
The utility reads a stats file with fixed headers, sums per-CPU rows into totals, prints cumulative or relative values, and loops with `sleep()` plus `lseek()` when an interval is supplied.

## State And Persistence Behavior
Read-only; local `last` stores prior totals for relative output.

## Dependencies And Integration Points
Uses global `selinux_mnt`, `/avc/cache_stats`, terminal `ioctl(TIOCGWINSZ)`, and SIGWINCH.

## Risks And Test Signals
Test header validation, no data, custom file path, relative deltas, cumulative mode, interval zero, SIGWINCH, and counter wrap/large values.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/avcstat.c -->
