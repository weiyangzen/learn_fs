# sources/user-network-fs/nfs-utils/support/include/xlog.h

## Purpose
Declares nfs-utils logging facilities, severity/debug facility masks, and printf-checked logging functions.

## Important APIs, Types, and Functions
`L_*` severities, `D_*` debug masks, `struct xlog_debugfac`, `export_errno`, `xlog_open()`, stderr/syslog toggles, config helpers, `xlog_enabled()`, `xlog()`, `xlog_warn()`, `xlog_err()`, `xlog_errno()`, and backend hook.

## Control Flow
Programs open logging, enable/disable facilities by numeric or string names, and emit severity/debug messages. Fatal severity exits in the implementation.

## State and Persistence Behavior
Implementation owns logging destination and enabled-facility process state. Messages persist to stderr/syslog depending on configuration.

## Dependencies and Integration Points
Used by nearly every support module. Format attributes catch mismatched printf arguments.

## Risks and Edge Cases
Mixing `D_` and `L_` values is documented as unsupported. Global logging state is process-wide.

## Test Signals
Test facility toggles, stderr/syslog routing, fatal behavior, errno formatting, and format warnings in builds.
