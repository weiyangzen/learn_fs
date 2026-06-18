# sources/user-network-fs/samba/source3/rpcclient/cmd_unixinfo.c

Purpose: this module exposes UNIXINFO RPC helpers in `rpcclient`: UID-to-SID conversion and passwd-style lookup by UID.

Important APIs, types, and functions: `cmd_unixinfo_uidtosid` calls `dcerpc_unixinfo_UidToSid` and formats `struct dom_sid` with `dom_sid_str_buf`; `cmd_unixinfo_getpwuid` calls `dcerpc_unixinfo_GetPWUid` and prints returned status, home directory, and shell. Results are `NTSTATUS`.

Control flow: each command requires exactly one UID argument, parses it with `atoi`, calls the generated RPC, separately checks transport status and server result, prints on success, and returns the meaningful status.

State and persistence: no local or remote mutation is performed. The server resolves identities from its configured Unix identity backend.

Dependencies and integration: depends on generated UNIXINFO NDR stubs, SID helpers, and `rpcclient.h`. Exported through `unixinfo_commands[]`.

Risks: `atoi` silently maps malformed or overflowing input to weak values. `cmd_unixinfo_getpwuid` contains a duplicated `if (!NT_STATUS_IS_OK(status))` check, making one branch unreachable in practice.

Test signals: test valid UID, nonexistent UID, malformed UID, permission failures, and output formatting for NULL or empty home/shell values.
