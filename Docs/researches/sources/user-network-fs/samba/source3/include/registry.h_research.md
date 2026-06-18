# sources/user-network-fs/samba/source3/include/registry.h

## Purpose
`registry.h` defines Samba's virtual Windows registry layer types, operation table, key handle structures, root key constants, well-known registry path strings, and registry key type identifiers.

## Important APIs, Types, And Control Flow
`struct registry_value` pairs a generated winreg type with a `DATA_BLOB`. `struct registry_ops` is the backend vtable for fetching/storing subkeys and values, creating/deleting subkeys, access checks, security descriptor get/set, and checking whether cached subkey/value containers need updates. `registry_key_handle` stores key type, full key name, granted access, and ops pointer. `registry_key` combines the handle with cached subkey/value containers and caller token. Constants define Windows root handles (`HKEY_LOCAL_MACHINE`, etc.), short key names (`HKLM`, `HKU`, etc.), many Samba/Windows registry paths for services, eventlog, shares, netlogon, TCP/IP, product options, printing, perflib, group policy, smbconf, and generic/performance key types.

## State And Persistence
The header models registry state persisted by registry backends, TDB files, virtual providers, or generated views. Runtime handles cache subkeys/values and security tokens; access-granted state is stored per handle.

## Dependencies And Integration Points
It depends on generated winreg NDR, DATA_BLOB, WERROR, security tokens/descriptors, and registry object containers declared elsewhere. It integrates with winreg RPC, Samba registry backends, printing registry keys, Group Policy, smb.conf registry storage, share definitions, eventlog, and performance counters.

## Risks And Test Signals
Risks include backend ops not honoring access masks, stale cached subkey/value containers, key string normalization bugs, lazy delete semantics differing by backend, and security descriptor persistence errors. Test signals include winreg create/open/delete/enumerate/set/get flows, access-denied cases, security descriptor round trips, printing key updates, smbconf registry operations, performance key reads, and cache invalidation through `subkeys_need_update()`/`values_need_update()`.
