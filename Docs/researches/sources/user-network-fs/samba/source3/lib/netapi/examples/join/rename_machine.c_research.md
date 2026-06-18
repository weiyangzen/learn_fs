# sources/user-network-fs/samba/source3/lib/netapi/examples/join/rename_machine.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/rename_machine.c

Purpose: Demonstrates renaming a domain-joined machine with `NetRenameMachineInDomain()`.

Important APIs/types/functions: Gets username/password from the libnetapi context and calls `NetRenameMachineInDomain(host, new_name, username, password, flags)`.

Control flow: Parses host, new machine name, and optional flags, retrieves credentials, calls the rename API, reports errors, and releases resources.

State and persistence behavior: Mutates domain/local computer name state and generally requires reboot or follow-up system changes.

Dependencies and integration points: Related to GUI hostname-change flow, though the GUI has this path mostly disabled.

Risks: Credentials are required; incorrect names can break domain trust. Flag parsing uses simple integer conversion.

Test signals: Rename a disposable joined machine and verify join information/DNS/account state after reboot.
