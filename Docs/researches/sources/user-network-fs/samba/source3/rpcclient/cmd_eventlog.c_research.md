# sources/user-network-fs/samba/source3/rpcclient/cmd_eventlog.c

## Purpose
`cmd_eventlog.c` provides rpcclient commands for Windows Event Log RPC operations: opening logs, reading records, querying record counters, writing test events, registering event sources, backing up logs, and querying log metadata.

## Important APIs, types, and functions
- `get_eventlog_handle()` opens a named log with `OpenEventLogW`.
- `cmd_eventlog_readlog()` reads records with `ReadEventLogW`, resizes the buffer on `BUFFER_TOO_SMALL`, decodes `EVENTLOGRECORD` structures with NDR, and prints debug dumps.
- `cmd_eventlog_numrecords()` and `cmd_eventlog_oldestrecord()` query counters.
- `cmd_eventlog_reportevent()` and `cmd_eventlog_reporteventsource()` write test information events.
- `cmd_eventlog_registerevsource()` registers and deregisters an event source named `rpcclient`.
- `cmd_eventlog_backuplog()` prefixes the requested path with `\\??\\` and calls `BackupEventLogW`.
- `cmd_eventlog_loginfo()` performs a two-step `GetLogInformation` buffer-size query.

## Control flow
Most commands validate arguments, open a log handle, call one or more generated eventlog RPC stubs, translate either transport or operation `NTSTATUS`, and close or deregister the handle on exit. Readlog loops backward/sequentially until the server returns end-of-file or another non-OK result, decoding records from the returned byte buffer using record length fields.

## State and persistence behavior
Read and query commands are read-only. Report-event commands append records to the remote event log, register-source touches server event-source state for the session, and backup-log writes a server-side backup file path. No local persistent state is stored.

## Dependencies and integration points
The module depends on generated EVENTLOG stubs and structures, LSA string initialization, NDR decoding of `EVENTLOGRECORD`, policy handles, and rpcclient command registration.

## Risks and edge cases
- Event writing and backup commands mutate remote state and can require administrative rights or valid server-local paths.
- `cmd_eventlog_registerevsource()` accepts a logname argument but does not use it when registering `rpcclient`.
- `cmd_eventlog_loginfo()` initially allocates a zero-length buffer and relies on server `BUFFER_TOO_SMALL` behavior.
- Readlog trusts record length fields from server data; malformed lengths can affect loop progress.
- Some error paths return without closing handles after transport errors inside read loops.

## Test signals
Against a test eventlog server, verify readlog buffer resizing, numrecords/oldestrecord output, reportevent/reporteventsource record creation, backup path handling, register/deregister behavior, and permission-denied cases.
