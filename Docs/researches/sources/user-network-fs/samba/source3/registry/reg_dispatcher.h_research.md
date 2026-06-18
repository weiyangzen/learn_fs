# sources/user-network-fs/samba/source3/registry/reg_dispatcher.h

## Purpose
`reg_dispatcher.h` declares the registry frontend dispatch helpers implemented in `reg_dispatcher.c`.

## Important APIs, Types, And Functions
It exposes store, create/delete, fetch, access-check, security descriptor, and cache freshness functions for `struct registry_key_handle`, `struct regsubkey_ctr`, and `struct regval_ctr`.

## Control Flow
Callers use these declarations after opening a registry key handle. The implementation routes each operation through the handle's selected `registry_ops` table or applies a default.

## State And Persistence
The header contains no state. The implementation works against backend state and transient talloc-allocated security descriptors.

## Dependencies And Integration Points
The declarations assume registry core types, `WERROR`, `TALLOC_CTX`, `security_descriptor`, and `security_token` are available through surrounding includes. It is an internal boundary between registry frontend code and backend ops tables.

## Risks And Test Signals
Compile coverage should include consumers that include this header in normal registry translation units. Behavioral tests belong to `reg_dispatcher.c`, with emphasis on missing callback defaults and security descriptor fallback.
