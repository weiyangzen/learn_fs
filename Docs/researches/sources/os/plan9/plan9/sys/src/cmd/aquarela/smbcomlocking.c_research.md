# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomlocking.c

Server handler for `SMB_COM_LOCKING_ANDX`.

Key functions:
- `getlock` parses small or large lock records into pid, offset, and length.
- `smbcomlockingandx` parses AndX header, fid, lock type, timeout, unlock count, lock count, validates unsupported options, applies unlocks, applies locks, rolls back partial locks on conflict, and chains or replies.

Interactions:
- Uses `smbsharedfilelock` and `smbsharedfileunlock`.
- Uses `smbchaincommand` for AndX continuation.

Notable details:
- Timeout, oplock, and nonzero locktype features are not implemented.
- The parsed lock record pid is logged but calls use `h->pid` for ownership.
