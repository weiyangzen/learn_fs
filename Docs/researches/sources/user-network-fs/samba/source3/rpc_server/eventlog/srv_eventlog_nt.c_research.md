# sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_nt.c

Purpose: Event Log RPC server implementation for opening, reading, clearing, querying, and writing records to Samba eventlog TDB files, plus server initialization that ensures backing registry keys exist.

Important APIs/types/functions: `EVENTLOG_INFO`, `elog_open`, `elog_close`, `elog_check_access`, `get_num_records_hook`, `sync_eventlog_params`, `_eventlog_OpenEventLogW`, `_eventlog_ReadEventLogW`, `_eventlog_ClearEventLogW`, `_eventlog_GetOldestRecord`, `_eventlog_GetNumRecords`, `_eventlog_GetLogInformation`, `evlog_report_to_record`, `_eventlog_ReportEventW`, and `eventlog_init_server`.

Control flow: open validates the requested log against `lp_eventlog_list`, opens the TDB as root, falls back to Application in some missing-file cases, checks file ACL access using a synthetic connection and `se_access_check`, creates a policy handle, syncs MaxSize/Retention from HKLM eventlog registry values, and prunes records. Read validates seek/sequential and direction flags, pulls records from the current or requested record number, NDR-encodes each `EVENTLOGRECORD`, respects caller buffer size, and advances `current_record`.

State/persistence behavior: policy handles own `EVENTLOG_INFO` and close TDBs through a destructor. Records and counters live in eventlog TDBs; retention/max-size settings are copied from registry into TDB keys. Clear reopens the TDB with truncate semantics when write access is granted.

Dependencies/integration: integrates eventlog library helpers, winreg internal RPC client calls, security descriptors, VFS ACL access, generated eventlog NDR, global messaging context, and `eventlog_init_winreg`.

Risks/test signals: access checks depend on filesystem ACLs plus a SYSTEM ACE, and root maps to the system token. Read buffer sizing and record pointer updates are protocol-sensitive. Many ANSI/backup/cluster methods are unimplemented fault stubs. Tests should cover open fallback, ACL denial, registry sync failure, zero-byte read size probing, forward/backward reads, clear permissions, record reporting, and server init key creation.
