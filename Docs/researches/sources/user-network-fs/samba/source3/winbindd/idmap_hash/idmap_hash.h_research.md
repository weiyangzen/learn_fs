# sources/user-network-fs/samba/source3/winbindd/idmap_hash/idmap_hash.h

## Purpose
This header provides small helper macros and the name-map lookup prototypes used by the deprecated hash idmap/NSS-info module. Despite the include guard name `_LWOPEN_H`, it belongs to the `idmap_hash` backend and exposes map-file key/value lookup helpers.

## Important APIs, Types, And Functions
The header defines `BAIL_ON_NTSTATUS_ERROR`, `BAIL_ON_PTR_NT_ERROR`, and `PRINT_NTSTATUS_ERROR`. It declares `mapfile_lookup_key(TALLOC_CTX *, const char *value, char **key)` and `mapfile_lookup_value(TALLOC_CTX *, const char *key, char **value)`.

## Control Flow
The macros are goto-based error handling helpers. `BAIL_ON_NTSTATUS_ERROR` jumps to `done` on a failing NT status. `BAIL_ON_PTR_NT_ERROR` sets an NT status based on pointer nullness, logging and jumping to `done` if allocation failed. The prototypes connect `idmap_hash.c` with `mapfile.c`.

## State And Persistence
The header itself has no state. It participates in map-file access where `mapfile.c` uses a static `FILE *` and an smb.conf parameter for the file path.

## Dependencies And Integration
Consumers must have Samba `NTSTATUS`, debug logging, and talloc types available. The macros assume the caller has a `done:` label and a writable status variable named in the macro argument, so they are tightly coupled to local function structure.

## Risks And Test Signals
Macro-based control flow can hide ownership and cleanup paths. Tests should compile all consumers with warnings enabled and exercise both map-file lookup directions. The misleading include guard name can collide with unrelated historical `lwopen` headers if one exists in the include path.
