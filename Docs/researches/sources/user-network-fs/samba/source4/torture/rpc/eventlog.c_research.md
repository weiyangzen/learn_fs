# sources/user-network-fs/samba/source4/torture/rpc/eventlog.c

## Purpose
This file implements the `rpc.eventlog` smbtorture suite for Windows Event Log RPC operations. It opens a log handle, reads and decodes event records, reports a new event, flushes, clears, queries log metadata, and tests backup-log path behavior.

## Important APIs, Types, And Functions
`torture_rpc_eventlog()` registers tests on `ndr_table_eventlog`. `get_policy_handle()` opens the `"dns server"` event log with `eventlog_OpenEventLogW`. `init_lsa_String()` prepares UTF-16 byte lengths for `lsa_String` inputs. Test functions call `dcerpc_eventlog_GetNumRecords_r`, `ReadEventLogW_r`, `ReportEventW_r`, `FlushEventLog_r`, `ClearEventLogW_r`, `GetLogInformation_r`, `OpenBackupEventLogW_r`, `BackupEventLogW_r`, and `CloseEventLog_r`.

## Control Flow
Each test opens a fresh event log handle, performs one scenario, and closes the handle. `test_ReadEventLog()` first confirms an invalid zero-flag read, then repeatedly probes with zero bytes to get `NT_STATUS_BUFFER_TOO_SMALL`, reallocates to the server-reported size, reads records backwards/sequentially, and unmarshals user-marshalled `EVENTLOGRECORD` blobs. `test_GetLogInformation()` verifies invalid level handling, then repeats at level 0 using the returned buffer size. `test_BackupLog()` verifies path syntax failure, successful NT object-path backup, name collision on duplicate backup, then opening the backup log.

## State And Persistence Behavior
`test_ReportEventLog()` writes an informational event into the target log. `test_ClearEventLog()` clears the log and is marked `dangerous`. `test_BackupLog()` creates a backup file at `\??\C:\samrtorturetest` and intentionally verifies duplicate-name collision; it is skipped against Samba modes. Handle state is explicit and closed in every normal path, but assertion failures before close may leave handles server-side until the connection is torn down.

## Dependencies And Integration Points
The file depends on generated eventlog NDR structures and the torture RPC framework. It also uses NDR record parsing (`ndr_pull_EVENTLOGRECORD`), `dump_data()`, `NDR_PRINT_DEBUG`, time functions, and Samba parameter settings for server-family skips.

## Risks And Edge Cases
The log name `"dns server"` assumes the target supports that event log. Clearing a real log is destructive. Backup tests can leave files on the server and use Windows-specific NT path semantics. Read-loop logic increments `offset` while also using sequential-read flags, so behavior is tied to server compatibility. `torture_rpc_eventlog()` has a visible typo in the registered test name `"GetLogIntormation"`, which affects test selection names.

## Test Signals
Success is signaled by exact NTSTATUS/WERROR expectations: invalid read parameters, buffer-too-small probes, successful event decode, access denied on flush, successful clear, invalid information level, backup path syntax errors, duplicate backup collision, and successful close operations.
