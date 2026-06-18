# sources/user-network-fs/samba/source3/passdb/pdb_tdb.h

## Purpose
`pdb_tdb.h` is the public header for registering the TDB-backed `tdbsam` passdb backend.

## Important APIs, Types, And Functions
The header declares `pdb_tdbsam_init(TALLOC_CTX *)`. The implementation registers the backend name `tdbsam`.

## Control Flow
There is no executable control flow in the header. Include guards prevent duplicate inclusion.

## State And Persistence
The header has no state. It exposes an initializer for a backend whose persistent state is `passdb.tdb`.

## Dependencies And Integration Points
Consumers include this header for static or module registration of the TDB passdb backend. The declaration assumes `NTSTATUS` and `TALLOC_CTX` are already visible.

## Risks
The header is intentionally narrow. Build/link failures are the primary signal for declaration drift. Runtime behavior and persistent-state risks are in `pdb_tdb.c`.

## Test Signals
Build/link tests should verify `pdb_tdbsam_init()` resolves. Module registry tests should verify the backend can be selected as `tdbsam`.
