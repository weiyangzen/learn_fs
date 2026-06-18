# sources/test-tools/stress-ng/stress-acct.c

## Purpose
`stress-acct.c` implements the `acct` stressor, exercising Linux process accounting via `acct()` and reading generated accounting records.

## Important APIs, Types, And Functions
`stress_acct_supported` requires `CAP_SYS_PACCT`. `stress_acct` creates a temp accounting file, enables accounting with `acct(filename)`, forks/kills short-lived children, reads `struct acct_v3` records, increments bogo ops when records show `AXSIG`, truncates the file above 16 MiB, and disables accounting with `acct(NULL)`. `stress_acct_info` registers the stressor or an unimplemented stub depending on feature macros.

## Control Flow
After temp setup and sync-start wait, the loop checks file size, enables accounting, forks a child that exits immediately, kills/waits it from the parent, reads available accounting records from the file descriptor, validates accounting version once, then disables accounting. The loop continues while the stressor should run.

## State And Persistence
It creates a temporary accounting file and toggles system-wide process accounting to point at that file. It truncates the file to bound growth and removes it during cleanup. The accounting setting is intended to be disabled each iteration, but abnormal termination could leave accounting enabled until cleanup or external correction.

## Dependencies And Integration Points
It depends on Linux `acct`, `sys/acct.h`, `acct_v3`, `CAP_SYS_PACCT`, temp-file helpers, sync-start, kill/wait helpers, and file I/O shims. It is classified as `CLASS_OS` and `VERIFY_NONE` because support is privilege- and kernel-dependent.

## Risks
Process accounting is global, privileged state; running this stressor can interfere with other accounting users. The code reads from a descriptor after writes by the kernel; file offset behavior is important for seeing records. Feature guards limit implementation to Linux with v3 accounting support.

## Test Signals
Support checks should skip without `CAP_SYS_PACCT`. With privileges, bogo ops indicate accounting records with signal-exit flags were read. Failures show as `acct()` errors, unexpected accounting version warnings, or cleanup leaving accounting enabled.
