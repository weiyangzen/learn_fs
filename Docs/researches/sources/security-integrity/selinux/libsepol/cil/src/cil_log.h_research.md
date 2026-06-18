# sources/security-integrity/selinux/libsepol/cil/src/cil_log.h

## Purpose
`cil_log.h` declares CIL internal logging helpers.

## Important APIs, Types, And Functions
It defines `MAX_LOG_SIZE` as 512 and declares formatted functions `cil_vlog` and `cil_log`, plus `cil_get_log_level`. The log handler and setter for log level are declared through the public CIL API rather than here.

## Control Flow
No executable control flow exists. GCC format attributes provide compile-time checking for printf-style calls.

## State And Persistence Behavior
No state is owned in the header. The implementation maintains process-global handler and log level.

## Dependencies And Integration Points
It includes `<cil/cil.h>` for `enum cil_log_level`. All CIL sources that need diagnostics include this header.

## Risks And Edge Cases
Changing `MAX_LOG_SIZE` affects truncation and stack buffer size in `cil_vlog`. Missing format attributes would reduce compiler coverage of logging calls.

## Test Signals
Build warnings for format misuse and logging unit tests are the primary signals.
