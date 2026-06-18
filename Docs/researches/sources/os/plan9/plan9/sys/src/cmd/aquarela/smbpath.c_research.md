# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbpath.c

Path split helper for SMB paths.

Key function:
- `smbpathsplit` splits a path at the last `/`, returning allocated directory and base-name strings.

Behavior:
- No slash: directory is `/`, name is whole path.
- Root slash: directory is `/`, name is after slash.
- Nested path: directory is substring before last slash.

Interactions:
- Used by delete and rename handlers.

Notable details:
- Caller owns both returned strings.
