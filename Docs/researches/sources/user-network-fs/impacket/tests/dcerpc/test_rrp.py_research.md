# sources/user-network-fs/impacket/tests/dcerpc/test_rrp.py

Purpose: broad Remote Registry Protocol (`rrp`) integration tests covering root-key opens, key/value create/query/delete, enumeration, security, save/restore/load/unload, performance hives, and multi-value queries.

Important APIs and functions: `RRPTests` binds `rrp.MSRPC_UUID_RRP` over `\PIPE\winreg`. `connect_scmr()`, `open_scmanager()`, and `start_rrp_service()` use SCMR over `\pipe\svcctl` to start `RemoteRegistry` before RRP connection. `open_local_machine()` opens HKLM with WOW64 and enumerate rights. Tests cover many raw/helper APIs including `OpenClassesRoot`, `OpenCurrentUser`, `OpenLocalMachine`, `OpenPerformanceData`, `OpenUsers`, `BaseRegCloseKey`, `BaseRegCreateKey`, `BaseRegSetValue`, `BaseRegDeleteValue`, `BaseRegDeleteKey`, `BaseRegEnumKey`, `BaseRegEnumValue`, `BaseRegFlushKey`, `BaseRegGetKeySecurity`, `BaseRegOpenKey`, `BaseRegQueryInfoKey`, `BaseRegQueryValue`, `BaseRegReplaceKey`, `BaseRegRestoreKey`, `BaseRegSaveKey`, `BaseRegSaveKeyEx`, `BaseRegGetVersion`, `OpenCurrentConfig`, `OpenPerformanceText`, `OpenPerformanceNlsText`, `BaseRegQueryMultipleValues`, `BaseRegQueryMultipleValues2`, `BaseRegDeleteKeyEx`, `BaseRegLoadKey`, and `BaseRegUnLoadKey`.

Control flow: setup initializes `rrp_started=False`. `connect()` starts RemoteRegistry once per test via SCMR, then delegates to `DCERPCTests.connect()`. Mutation tests create `BETO` key and `BETO2` value under HKCR, query the value, delete value/key, and assert round-trip data. Save/load tests save hives to files under `%SystemRoot%\System32`, load them under temporary subkeys, unload, and delete files over SMB ADMIN$.

State and persistence behavior: high statefulness. It starts a Windows service, creates/deletes registry keys and values, saves hive files (`BETUSFILE2`, `SEC`) on the remote admin share, loads/unloads a temporary hive key, and opens sensitive keys including `SECURITY` and `SYSTEM\CurrentControlSet\Control\Lsa\JD`. Cleanup exists for most generated artifacts but is not consistently protected by `finally`.

Dependencies and integration points: integrates SCMR service-control RPC, RRP named-pipe RPC, SMB file deletion through the underlying transport, remote admin privileges, RemoteRegistry service, and registry security policy.

Risks: should run only on disposable or dedicated test systems. Failed cleanup can leave registry keys, loaded hives, files in `System32`, or a started RemoteRegistry service. Querying sensitive LSA/SECURITY hives requires high privilege. Some tests use broad `MAXIMUM_ALLOWED`; expected errors for replace/restore depend on file availability.

Test signals: strong coverage for RRP marshalling, helper parity, value encoding/decoding, buffer fields, WOW64 access masks, security descriptors, hive save/load paths, SMB integration for cleanup, and NDR/NDR64 compatibility.
