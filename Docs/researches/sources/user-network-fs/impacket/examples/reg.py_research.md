# sources/user-network-fs/impacket/examples/reg.py

## Purpose

`reg.py` is a remote Windows registry manipulation tool modeled after `reg.exe`. It authenticates over SMB, starts or triggers the RemoteRegistry service when needed, binds to the Remote Registry Protocol (`\pipe\winreg`), and supports query, add, delete, save, and backup operations.

## Important APIs, Types, and Functions

`RemoteOperations` owns service-control and winreg RPC connections, tracks whether RemoteRegistry was disabled or stopped, and restores service state in `finish()`. `RegHandler` owns credentials, SMB login, action dispatch, and registry operations. Key methods include `connect()`, `run()`, `triggerWinReg()`, `save()`, `query()`, `add()`, `delete()`, `__strip_root_key()`, `__print_key_values()`, `__print_all_subkeys_and_entries()`, and `__parse_lp_data()`.

## Control Flow

The CLI builds subcommands for `query`, `add`, `delete`, `save`, and `backup`, parses target/auth/connection options, prompts for a password when needed, and instantiates `RegHandler`. `run()` logs into SMB, creates `RemoteOperations`, attempts `enableRegistry()`, falls back to opening the `\winreg` named pipe to trigger startup, then dispatches the requested action. Queries open a root hive and either read a value, default value, direct values/subkeys, or recursively enumerate. Add can create a volatile or persistent key or set typed value data. Delete removes keys, one value, default value, or all values. Save and backup call `hBaseRegSaveKey()` to a UNC path visible to the target.

## State and Persistence Behavior

Remote state can change substantially: RemoteRegistry may be started and possibly reconfigured from disabled to demand start, registry keys and values can be created/deleted, and registry hives can be saved to a remote UNC path. `RemoteOperations.finish()` tries to stop and disable RemoteRegistry only if it changed those states. Local state is limited to stdout/logging and interactive password input.

## Dependencies and Integration Points

It integrates with Impacket `SMBConnection`, DCE/RPC transports, `rrp`, `scmr`, `rpcrt`, Windows service control, and `ERROR_NO_MORE_ITEMS`. Kerberos, AES keys, NTLM hashes, target IP override, and SMB port 139/445 are supported.

## Risks and Edge Cases

Registry writes and deletes are high-impact and not transactionally rolled back. The fallback named-pipe trigger assumes a target behavior and sleeps for one second. Recursive queries may hit access denied or bad stub data and skip branches. `REG_BINARY` input is padded if odd-length hex is provided. `save()` writes on the target side to a UNC path, so permissions and path interpretation can fail. Service-state restoration can fail if the process is interrupted after remote changes.

## Test Signals

Mock tests should cover root-key parsing, value type conversion, binary padding, `REG_MULTI_SZ` construction, delete-mode dispatch, service state restoration decisions, and recursive enumeration error handling. Integration tests require a Windows host and should verify query, volatile/persistent add, delete variants, Kerberos/hash login, RemoteRegistry disabled/start/restore behavior, and hive save to a controlled share.
