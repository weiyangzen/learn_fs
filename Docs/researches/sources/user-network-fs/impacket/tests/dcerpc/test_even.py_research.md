# sources/user-network-fs/impacket/tests/dcerpc/test_even.py

Purpose: validates legacy EventLog RPC (`even`) client calls against `\PIPE\eventlog`.

Important APIs and functions: class `RRPTests` in this file binds `even.MSRPC_UUID_EVEN` with packet privacy. It exercises raw and helper calls for `ElfrOpenBELW`, `ElfrOpenELW`, `ElfrRegisterEventSourceW`, `ElfrReadELW`, `ElfrClearELFW`, `ElfrBackupELFW`, raw `ElfrReportEventW`, `hElfrNumberOfRecords`, and `hElfrOldestRecordNumber`.

Control flow: tests open the Security log or a bogus backup log path, then issue read, clear, backup, report, count, and oldest-record requests. Many paths assert expected Windows errors such as missing backup file, invalid backup path, or access denied.

State and persistence behavior: mostly read-only. Clear, backup, and report calls are attempted but expected to fail due to invalid path or access denial, preventing actual log mutation. Handles are not explicitly closed in this suite.

Dependencies and integration points: requires eventlog named pipe, authenticated access, and sufficient rights to read Security log for success paths. Uses Impacket `even` NDR structures and helper functions.

Risks: Security log access is privilege-sensitive. Expected error text can vary. Class name `RRPTests` is misleading and can confuse test reporting.

Test signals: confirms legacy eventlog handle creation, read buffer handling, expected error unmarshalling, and helper parity for NDR/NDR64 named-pipe transports.
