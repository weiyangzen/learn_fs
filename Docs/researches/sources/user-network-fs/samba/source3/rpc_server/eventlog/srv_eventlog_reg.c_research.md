# sources/user-network-fs/samba/source3/rpc_server/eventlog/srv_eventlog_reg.c

Purpose: initializes Windows-compatible eventlog registry keys used by the Event Log RPC server.

Important APIs/types/functions: `eventlog_init_winreg` opens `HKLM\SYSTEM\CurrentControlSet\Services\Eventlog`, enumerates existing subkeys, creates missing configured eventlog keys, and writes default values.

Control flow: the function opens the top-level Eventlog key through the internal winreg RPC client using the system session. It enumerates existing log subkeys, then for every configured log name from `lp_eventlog_list`, skips existing keys and creates missing keys. It writes `MaxSize`, `Retention`, `PrimaryModule`, `File`, and `Sources`, then creates a nested source-specific subkey with `CategoryCount` and `CategoryMessageFile`.

State/persistence behavior: persistent state is the Samba registry backend. Default values are 512 KiB max size and one week retention. The `File` value points at `%SystemRoot%\system32\config\<log>.tdb`.

Dependencies/integration: depends on generated winreg client stubs, `cli_winreg_int` helpers, Samba auth system session, messaging context, loadparm eventlog list, and registry policy handles.

Risks/test signals: status from several set-value calls is overwritten by later calls before being checked, so write failures can be masked unless the final call fails. The nested subkey name is formed by appending the log name again to the current key path. Tests should verify idempotent startup, exact registry values, missing top-level key behavior, configured logs with existing subkeys, and cleanup of opened handles.
