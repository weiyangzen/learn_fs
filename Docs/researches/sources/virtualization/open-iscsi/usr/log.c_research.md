# File Research: sources/virtualization/open-iscsi/usr/log.c

## Purpose
`log.c` implements open-iscsi logging for both foreground CLI-style programs and daemon mode. Daemon mode uses SysV shared memory and semaphores to queue log messages from the main process to a logging child that writes to syslog, avoiding blocking syslog calls in sensitive daemon paths.

## Main Components
- Global logging state: `log_name`, `log_level`, global `struct logarea *la`, selected `log_func`, and private logging-child stop flag.
- `logarea_init()` creates shared memory for metadata, circular message storage, a staging buffer, and a semaphore.
- `free_logarea()` removes semaphore and shared-memory segments.
- `log_enqueue()` appends a formatted message into the shared circular area, rewinding at end and dropping messages if there is not enough space before the head.
- `log_dequeue()` copies the current head message into the staging buffer, advances the head, and clears consumed memory.
- `log_do_log_daemon()` takes the semaphore, enqueues a message, and releases the semaphore.
- `log_do_log_std()` prints `LOG_INFO` to stdout and other priorities to stderr with the program name prefix.
- `log_warning()`, `log_error()`, `log_debug()`, `log_info()`, and `sess_log_connect()` are the public wrappers.
- `log_flush()` drains queued daemon messages to syslog.
- `log_init()` selects the logging backend; for daemon logging it opens syslog, initializes shared memory, forks the logging child, daemonizes the child, installs signal handlers, and flushes once per second until SIGTERM.
- `log_close()` stops the logging child and cleans resources.

## Session Logging Behavior
`sess_log_connect()` prefixes messages with `sessionN` when a session is available and rate-limits reconnect logging according to `sess_reopen_log_freq` unless debug level is high.

## Integration Notes
The logging function pointer allows utilities to initialize stdout/stderr logging while `iscsid` uses daemon logging. The shared `struct logarea` layout is declared in `log.h`.

## Risk Notes
- The daemon log queue has fixed-size messages (`MAX_MSG_SIZE`) and can drop messages when the circular area is full.
- SysV semaphore key `SEMKEY` is fixed, so multiple daemon instances could contend if namespaces are not otherwise isolated.
- Logging from signal handlers is limited but still present for some signals; SIGPIPE handling is avoided in `iscsid.c` for loop prevention.
