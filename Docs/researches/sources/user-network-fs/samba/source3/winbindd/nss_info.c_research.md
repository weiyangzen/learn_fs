# sources/user-network-fs/samba/source3/winbindd/nss_info.c

## Purpose
This file implements the NSS-info plugin registry and domain-to-backend dispatch layer. NSS-info backends normalize account aliases for winbind/idmap integrations.

## Important APIs, Types, And Functions
Global registries are `backends`, `default_backend`, and `nss_domain_list`. Public functions are `smb_register_idmap_nss`, `nss_map_to_alias`, `nss_map_from_alias`, and `nss_close`. Internal helpers include `nss_get_backend`, `parse_nss_parm`, `nss_domain_list_add_domain`, `nss_init`, and `find_nss_domain`.

## Control Flow
Backends register by interface version and unique name. `nss_init` lazily ensures the `template` backend is registered, parses `lp_winbind_nss_info()` entries as `backend[:domain]`, probes missing modules, records the first domainless backend as default, initializes domain entries, and marks the system initialized. `find_nss_domain` initializes on demand, searches for a configured domain, or creates a new domain entry using the default backend. Mapping calls dispatch through the selected backend's `map_to_alias` or `map_from_alias`. `nss_close` walks configured domains, calls each backend close function, and frees entries.

## State And Persistence
State is process-global and memory-only. Once `nss_initialized` is true, subsequent config changes are not reparsed by this file. Backend-specific state hangs off `struct nss_domain_entry`.

## Dependencies And Integration
It depends on `nss_info.h`, Samba module probing, static init, configuration (`lp_winbind_nss_info`), DLIST macros, and talloc allocation. Hash and template NSS-info backends register through this API.

## Risks And Test Signals
Test version mismatch, duplicate backend registration, invalid config strings, missing modules, default backend behavior, per-domain init failures and retry, map dispatch, and `nss_close`. The global one-time init means reload behavior needs attention; after close, `nss_initialized` is not reset in this file.
