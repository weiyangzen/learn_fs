# sources/user-network-fs/samba/source3/utils/net_sam.c

## Purpose
Provides local `net sam` administration for Samba passdb/SAM state: user fields and flags, account policies, privilege rights, Unix group mapping, group creation/deletion, group membership, listing/showing entries, and optional LDAP provisioning.

## Important APIs, Types, and Functions
User updates use `struct samu`, `lookup_name()`, `pdb_getsampwsid()`, field setter callbacks, and `pdb_update_sam_account()`. Group and mapping paths use `GROUP_MAP`, `pdb_getgrgid()`, `pdb_new_rid()`, `sid_compose()`, and passdb group mapping APIs. Membership uses alias and domain group member APIs. Rights use `sec_privilege_id()`, `privilege_enum_sids()`, `grant_privilege_by_name()`, and `revoke_privilege_by_name()`. LDAP provisioning uses `fetch_ldap_pw()`, `smbldap_init()`, LDAP mods, passdb lookup, and Winbind ID allocation.

## Control Flow
`net_sam()` warns when not root and dispatches subcommands. `set` routes to common user string setters, account-control flag setters, password-must-change handling, or group/user comment updates. `policy`, `rights`, `list`, and membership commands each validate arguments and SID types before passdb calls. LDAP provisioning verifies `ldapsam` configuration, connects with the LDAP secret, then checks/creates default domain groups and Administrator/Guest entries.

## State and Persistence
Writes persistent passdb data, account policies, privilege assignments, group mappings, alias/group memberships, and optionally LDAP directory entries. Reads secrets from `secrets.tdb`, NSS users/groups, loadparm settings, and Winbind allocation state.

## Dependencies and Integration Points
Integrates passdb, LDAP schema helpers, Winbind, ID mapping, SAMR constants, local name/SID lookup, privilege APIs, and common `net_run_function()` dispatch. All commands are local transport.

## Risks
The file performs high-impact administrative mutations. Type checks reduce mistakes, but ambiguous names, backend capability differences, non-root operation, missing Winbind, or partial LDAP provisioning can cause inconsistent state. LDAP provisioning is sequential rather than transactional.

## Test Signals
Cover argument/type rejection, user field and flag updates, password-last-set toggling, policy list/show/set, rights list/grant/revoke, group map/unmap collisions, group create/delete, add/del/list membership, passdb failure paths, root warning, and LDAP provisioning for existing/missing defaults.
