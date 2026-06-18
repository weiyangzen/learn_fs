# sources/user-network-fs/samba/source3/registry/reg_init_smbconf.h

## Purpose
`reg_init_smbconf.h` declares the narrow smbconf registry initialization API.

## Important APIs, Types, And Functions
It exposes `WERROR registry_init_smbconf(const char *keyname)`.

## Control Flow
Callers pass a specific registry key or `NULL` for the default `KEY_SMBCONF` path. The implementation initializes common registry state and registers the smbconf backend only for that path.

## State And Persistence
The header has no state. The implementation may create the named registry key in persistent storage and updates the in-memory hook cache.

## Dependencies And Integration Points
Used by configuration tooling and loadparm-related code that needs registry-backed smb.conf data without full registry initialization.

## Risks And Test Signals
Compile coverage should ensure `WERROR` is available. Runtime tests should validate the null default and custom-key hook registration in the implementation.
