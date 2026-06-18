<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/destroy_netlogon_creds_cli.c -->
# sources/user-network-fs/samba/source3/utils/destroy_netlogon_creds_cli.c

## Purpose
`destroy_netlogon_creds_cli.c` is a targeted test utility that intentionally corrupts the stored netlogon client credential session key for a workstation/domain/DC tuple. It is used to exercise recovery and failure paths around `netlogon_creds_cli` state.

## Important APIs, types, and functions
- `main()` is the only function. It expects `cli_computer domain dc`.
- It initializes Samba config, loadparm, tevent, messaging, and opens the private `netlogon_creds_cli` db.
- `netlogon_creds_cli_set_global_db()` installs the opened db.
- `netlogon_creds_cli_context_global()` constructs the credential context for `cli_computer$`, workstation secure channel, DC, and domain.
- `netlogon_creds_cli_lock()` obtains the stored credential state, then the utility increments `creds->session_key[0]` and stores it back with `netlogon_creds_cli_store()`.

## Control flow
The program validates the argument count, initializes required Samba contexts, opens or creates the `netlogon_creds_cli` private database with `0600` permissions, creates a global credential context, locks/fetches credentials, mutates one byte of the session key, stores the corrupted state, frees the credential state, and exits 0 on success.

## State and persistence behavior
This utility deliberately persists corrupted netlogon credential state in Samba's private `netlogon_creds_cli` database. It is destructive for that credential tuple and should be run only in test contexts.

## Dependencies and integration points
It integrates with loadparm, messaging, dbwrap, private db path resolution, and `libcli/auth/netlogon_creds_cli.h`. The target state is later consumed by netlogon secure-channel clients.

## Risks and edge cases
- It has no confirmation prompt and intentionally damages authentication state.
- The machine account name is formed by appending `$` to `argv[1]`.
- A missing existing credential record causes lock/fetch failure rather than creating a useful test state.
- DB open uses create mode, but the semantic target must already be meaningful to the netlogon credential layer.

## Test signals
Success is exit 0 after `netlogon_creds_cli_store()`. Downstream tests should observe secure-channel credential verification or recovery failures caused by the modified session key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/destroy_netlogon_creds_cli.c -->
