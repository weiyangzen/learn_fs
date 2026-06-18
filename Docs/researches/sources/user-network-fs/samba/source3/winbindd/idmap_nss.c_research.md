# sources/user-network-fs/samba/source3/winbindd/idmap_nss.c

## Purpose
The `nss` idmap backend maps between Unix users/groups known to the local NSS stack and SIDs resolved through winbind name/SID lookup calls. It is read-only in practice: it queries libc `getpw*`/`getgr*` and winbind rather than persisting mappings.

## Important APIs, Types, And Functions
`struct idmap_nss_context` stores the owning `idmap_domain` and `use_upn` config flag. `idmap_nss_int_init` creates context and installs a messaging filtered read for smb.conf reloads. `idmap_nss_unixids_to_sids` maps UID/GID to names and then to SIDs. `idmap_nss_sids_to_unixids` maps SIDs to names and then to local passwd/group entries. `idmap_nss_init` registers the backend.

## Control Flow
Initialization creates context, stores it in `dom->private_data`, and subscribes to `MSG_SMB_CONF_UPDATED` so `use_upn` can be refreshed. UID/GID lookup calls `getpwuid` or `getgrgid`, optionally parses UPN or domain separator components, and calls `winbind_lookup_name` while winbind recursion is temporarily enabled via `winbind_on/off`. SID lookup calls `winbind_lookup_sid`, rejects SIDs whose domain does not match the configured idmap domain, optionally builds `DOMAIN\name`, and then uses `Get_Pwnam_alloc` or `getgrnam`.

## State And Persistence
State is memory-only. The backend depends on external NSS databases, winbind cache/domain state, and live smb.conf reload messages. It does not allocate or store mappings.

## Dependencies And Integration
The file integrates with Samba messaging, global messaging context, winbind client utilities, libc NSS, and idmap registration. It uses `lp_winbind_separator`, `idmap_config_bool`, and domain name comparisons.

## Risks And Test Signals
Test config reload of `use_upn`, UPN parsing with `@`, separator parsing with configured separator, mismatched domains, unavailable NSS records, wrong SID types, and recursion safety around `winbind_on/off`. The code mutates the `pw_name`/`gr_name` string when splitting at a separator or `@`, so tests should ensure the returned libc buffers are not reused unexpectedly in the same flow.
