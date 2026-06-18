# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreeconnectandx.c

Server handler for `SMB_COM_TREE_CONNECT_ANDX`.

Key behavior:
- Validates session state and allowed AndX commands.
- Parses flags, password length, UNC path, and service string.
- Optionally disconnects existing tree id when flags request it.
- Resolves service through `smbservicefind`, creates a tree mapping, and returns tid plus service type and filesystem name string `9p2000`.
- Chains if requested.

Interactions:
- Uses `smbservice.c` and tree id-map functions from other SMB support files.

Notable details:
- Accepts both IPC and disk tree services through service lookup.
