# sources/user-network-fs/samba/source3/passdb/pdb_util.c

## Purpose
`pdb_util.c` contains passdb utility helpers for creating and populating standard BUILTIN aliases: Users, Administrators, and Guests. These helpers bridge passdb alias creation, SID-to-GID mapping, winbind availability, and domain/local SID membership policy.

## Important APIs, Types, And Functions
`add_sid_to_builtin()` adds a member SID to an existing builtin alias using `pdb_add_aliasmem()`, treating `NT_STATUS_MEMBER_IN_ALIAS` as success and logging other failures. `pdb_create_builtin()` composes a BUILTIN SID from a RID and ensures the corresponding alias exists, either by asking the current passdb backend to create it or by using an existing SID-to-GID mapping when the backend is not responsible for BUILTIN.

`create_builtin_users()`, `create_builtin_administrators()`, and `create_builtin_guests()` create the standard aliases and add expected domain/local memberships. Users can include Domain Users for DC/domain-member roles. Administrators can include Domain Admins and local `DOMAIN\root`. Guests includes local Guest, local Guests, and for domain members the domain Guests group.

## Control Flow
`pdb_create_builtin()` composes `S-1-5-32-<rid>`. If the selected passdb backend is not responsible for BUILTIN, it resolves the BUILTIN SID to a gid with `sid_to_gid()` and calls `pdb_create_builtin_alias(rid, gid)`. If the backend is responsible, it checks `pdb_sid_to_id()` directly; a missing mapping means the alias likely does not exist, so the function requires nested groups and a live winbind ping before creating the builtin alias with gid 0.

The standard creation helpers call `pdb_create_builtin()` first. They then compose the relevant domain/local SIDs and call `add_sid_to_builtin()` for each expected member, returning early on significant failures. `create_builtin_administrators()` uses a temporary talloc context and `lookup_name()` to find the local `root` account SID before adding it if found.

## State And Persistence
Persistent state is maintained by the active passdb backend: builtin alias records and alias membership records. This file does not store data directly. Runtime state is limited to local SIDs, temporary talloc contexts, and lookup results.

The behavior depends on server role, global SAM SID/name, whether the backend claims BUILTIN responsibility, winbind nested-group configuration, and winbind availability.

## Dependencies And Integration Points
This file depends on passdb alias APIs, SID utilities, winbind helpers (`sid_to_gid()`, `winbind_ping()`), loadparm (`lp_winbind_nested_groups()`, `lp_server_role()`), global SID/name helpers, and LSA SID type lookup. It is typically used by setup or account-initialization code that ensures well-known BUILTIN groups exist with expected memberships.

## Risks
BUILTIN creation can fail if winbind is unavailable or nested groups are disabled while the backend is responsible for BUILTIN. Adding duplicate members is intentionally idempotent, but other membership failures propagate. Role-dependent behavior means domain-member and DC paths add domain SIDs while standalone paths do not. The root lookup is best-effort; failure to resolve `DOMAIN\root` does not fail administrator creation.

`pdb_create_builtin()` behaves differently depending on backend responsibility. Misreported `is_responsible_for_builtin` or broken idmap can create missing aliases, aliases with unsuitable gids, or protocol-unreachable errors during initialization.

## Test Signals
Tests should cover creation when backend is and is not responsible for BUILTIN, missing SID-to-GID mapping, winbind unavailable, nested groups disabled, duplicate alias membership, DC/domain-member/standalone role differences, root SID lookup success/failure, and all three standard aliases with expected member SIDs.
