# sources/user-network-fs/samba/source4/rpc_server/lsa/lsa_init.c

## Purpose

`lsa_init.c` builds and opens LSA policy handles. It connects to SAMDB and the privilege DB, collects stable domain metadata into `lsa_policy_state`, constructs the policy security descriptor, performs policy access checks, and implements `OpenPolicy`, `OpenPolicy2`, and `OpenPolicy3`.

## Important APIs, Types, and Functions

- `DCESRV_LSA_POLICY_SD_SDDL` defines the Windows-compatible policy object security descriptor.
- `dcesrv_lsa_policy_mapping` maps generic access bits to LSA policy rights.
- `dcesrv_lsa_get_policy_state()` initializes `struct lsa_policy_state`.
- `dcesrv_lsa_OpenPolicy3()` supports revision negotiation and advertises `LSA_FEATURE_TDO_AUTH_INFO_AES_CIPHER`.
- `dcesrv_lsa_OpenPolicy2()` creates the standard policy handle.
- `dcesrv_lsa_OpenPolicy()` wraps `OpenPolicy2` for the older IDL shape.

## Control Flow

`dcesrv_lsa_get_policy_state()` allocates a state, connects to SAMDB as the caller, connects to the privilege DB, gets default and forest base DNs, queries the domain object for SID/GUID/mixed-domain data, derives DNS names from canonical DNs, locates builtin and system containers, parses common authority SIDs, decodes the policy SDDL, maps generic access rights, and performs access checking. System-level callers bypass the descriptor to support local root/system use; other callers use `se_access_check()`.

`OpenPolicy2()` and `OpenPolicy()` are restricted to named pipe and local RPC transports. They reject non-null `attr->root_dir`, zero the output handle, build policy state, create a `LSA_HANDLE_POLICY`, steal the state under the handle, back-link `state->handle`, and return the wire handle.

`OpenPolicy3()` validates version input first. Version 1 returns revision 1 and the AES trusted-domain auth-info feature bit; other versions return `NT_STATUS_NOT_SUPPORTED`.

## State and Persistence Behavior

The file does not mutate database records. It opens database connections and snapshots identity/configuration data into policy state for later calls. The decoded security descriptor is held in memory and its DACL revision is forced to `SECURITY_ACL_REVISION_NT4`.

## Dependencies and Integration Points

Key dependencies include SAMDB connection helpers, `privilege_connect()`, LDB base DN helpers, SAMDB result extraction, system container discovery, `sddl_decode()`, generic access mapping, session user-level checks, and `se_access_check()`. The resulting state feeds policy queries, lookup, privilege operations, trusted-domain operations, DSSETUP role info, secrets, and forest trust handling.

## Risks and Edge Cases

- Missing SAMDB, privilege DB, domain DN, forest DN, builtin DN, or system DN prevents policy open.
- System callers intentionally bypass descriptor checks; changing this can break local service use.
- DNS names are derived by truncating canonical DN strings at the first slash.
- `OpenPolicy3()` feature negotiation is coupled to AES trust auth support in the main LSA implementation.

## Test Signals

Test named-pipe and local transports, rejected transports, null and non-null `root_dir`, `MAXIMUM_ALLOWED`, administrator/system/user/anonymous tokens, OpenPolicy3 supported and unsupported versions, malformed SAMDB metadata, and downstream policy query/lookup behavior that consumes initialized fields.
