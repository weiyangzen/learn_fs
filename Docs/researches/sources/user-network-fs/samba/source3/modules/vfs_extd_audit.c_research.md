# sources/user-network-fs/samba/source3/modules/vfs_extd_audit.c

## Purpose
`vfs_extd_audit.c` logs selected VFS operations to syslog and Samba debug logs for auditing.

## Important APIs, Types, And Functions
`audit_syslog_facility()` and `audit_syslog_priority()` parse `extd_audit` facility/priority parameters. Wrappers log connect, disconnect, mkdirat, openat, close, renameat, unlinkat, and fchmod around next VFS calls. Init registers a custom debug class.

## Control Flow
Connect delegates first, then opens syslog and logs. Operation wrappers usually build full paths, call the lower hook, and log success or failure. `audit_renameat()` preserves errno across logging and cleanup. Disconnect logs then delegates.

## State And Persistence
No per-handle state exists. Syslog/debug output is the persistent audit signal. The debug class id is process-global.

## Dependencies And Integration Points
It depends on syslog, loadparm `lp_syslog()`, Samba path helpers, next VFS hooks, and debug class registration.

## Risks
Coverage is selective. Some normal operations use high-severity debug macros, making logs noisy. Path formatting can be confusing in `openat`. If path allocation fails, the file operation fails too. Logs may expose sensitive names.

## Test Signals
Test facility and priority parsing, syslog-disabled behavior, connect/disconnect records, success/failure logs, errno preservation on rename, path allocation failure, and debug class setup.
