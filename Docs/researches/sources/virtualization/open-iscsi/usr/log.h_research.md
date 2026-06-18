# File Research: sources/virtualization/open-iscsi/usr/log.h

## Purpose
`log.h` declares the open-iscsi logging API and shared-memory queue structures.

## Exports
- Constants: `DEFAULT_AREA_SIZE` and `MAX_MSG_SIZE`.
- Global `log_level` and `struct logarea *la`.
- `struct logmsg` and `struct logarea` describing queued daemon log messages, circular buffer pointers, shared memory IDs, semaphore data, and staging buffer.
- `log_init()`, `log_close()`, `log_info()`, `log_warning()`, `log_error()`, `log_debug()`, `sess_log_connect()`, and backend functions `log_do_log_daemon()` and `log_do_log_std()`.
- A local `union semun` definition for SysV semaphore control calls.

## Integration Notes
The header includes `iscsid.h` and `initiator.h` because session-aware logging accepts `struct iscsi_session *`. Printf-format attributes are used on logging wrappers to let the compiler check format strings.

## Risk Notes
Including daemon and initiator headers makes this logging header relatively heavy and couples logging prototypes to session internals.
