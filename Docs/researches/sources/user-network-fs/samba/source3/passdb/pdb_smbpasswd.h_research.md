# sources/user-network-fs/samba/source3/passdb/pdb_smbpasswd.h

## Purpose
`pdb_smbpasswd.h` is the public header for registering the legacy smbpasswd passdb backend.

## Important APIs, Types, And Functions
The header declares `pdb_smbpasswd_init(TALLOC_CTX *)`. The implementation registers the backend name `smbpasswd` with Samba's passdb module registry.

## Control Flow
There is no executable control flow in the header. Include guards prevent duplicate inclusion.

## State And Persistence
The header has no state. It exposes an initializer for a backend whose persistent state is the smbpasswd flat file.

## Dependencies And Integration Points
Consumers include this header when they need the init symbol for static or module registration. It relies on existing declarations for `NTSTATUS` and `TALLOC_CTX`.

## Risks
The header does not expose any internal smbpasswd structures, which is good encapsulation. Build failures would indicate mismatch between the init declaration and implementation. Runtime risks are in the C implementation.

## Test Signals
Build/link tests should verify `pdb_smbpasswd_init()` is declared and resolves. Module registration tests should verify the backend can be registered and selected as `smbpasswd`.
