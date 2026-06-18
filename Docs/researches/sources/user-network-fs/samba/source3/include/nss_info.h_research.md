# sources/user-network-fs/samba/source3/include/nss_info.h

## Purpose
`nss_info.h` defines the pluggable NSS alias mapping interface used by winbind/idmap code. Backends translate account names to aliases and back on a per-domain basis, with a versioned registration contract.

## Important APIs, Types, And Control Flow
The interface version is `SMB_NSS_INFO_INTERFACE_VERSION`. `struct nss_function_entry` registers a backend name and method table. `struct nss_domain_entry` binds a configured domain to a backend, initialization status, and backend-specific state. `struct nss_info_methods` provides `init`, `map_to_alias`, `map_from_alias`, and `close_fn`. Public functions register backends (`smb_register_idmap_nss()`), perform domain-aware mappings (`nss_map_to_alias()`, `nss_map_from_alias()`), close the subsystem, and initialize the template backend.

## State And Persistence
State is held in linked lists of backend registrations and domain entries. Each domain can retain backend-specific state through `void *state`, with `init_status` recording whether setup succeeded. The header itself persists nothing; LDAP-capable backends may use external directory state.

## Dependencies And Integration Points
It depends on NTSTATUS, talloc, Samba list conventions, and optionally LDAP types, falling back to `void` for `LDAPMessage` when LDAP support is absent. It integrates with winbindd NSS information mapping, idmap configuration, and template alias handling.

## Risks And Test Signals
Risks include interface version mismatches, backend close functions cleaning shared state too broadly, stale per-domain state after reconfiguration, and LDAP/no-LDAP type compatibility. Test signals include backend registration with correct and incorrect versions, domain initialization failure caching, alias round trips, template backend initialization, close/reopen behavior, and builds with and without LDAP support.
