# sources/user-network-fs/samba/source4/rpc_server/lsa/lsa.h

## Purpose

`lsa.h` is the shared private header for the Samba4 LSA RPC endpoint implementation. It centralizes includes needed by the LSA server files, defines the policy-handle state structure, defines the internal handle type enum, and includes generated local prototypes.

## Important APIs, Types, and Functions

- `struct lsa_policy_state` is the central per-policy-handle state used across `lsa_init.c`, `dcesrv_lsa.c`, and `lsa_lookup.c`.
- `enum lsa_handle` assigns private handle type tags: `LSA_HANDLE_POLICY`, `LSA_HANDLE_ACCOUNT`, `LSA_HANDLE_SECRET`, and `LSA_HANDLE_TRUSTED_DOMAIN`.
- `rpc_server/lsa/proto.h` exposes generated prototypes for the LSA implementation files.

`lsa_policy_state` stores the DCERPC handle, SAMDB and privilege DB connections, domain/forest/builtin/system DNs, NetBIOS and DNS names, domain GUID/SID, common authority SIDs, mixed-domain state, decoded policy security descriptor, and granted access mask.

## Control Flow

This header implements no runtime control flow. Its structure layout drives how `dcesrv_lsa_get_policy_state()` initializes policy state, how main LSARPC handlers access databases and domain identity, and how lookup code determines authority scopes.

## State and Persistence Behavior

The header defines in-memory state only. `lsa_policy_state` references persistent stores through `sam_ldb` and `pdb`, but persistence is implemented by the C files. The state is allocated during policy open and is either stored under a policy handle or cached on a secure connection for handle-less lookups.

## Dependencies and Integration Points

The include list pulls in DCERPC server types, common RPC helpers, auth/session types, SAMDB, LDAP NDR helpers, LDB errors, security helpers, auth crypto helpers, secrets DB access, LDB utilities, DSSETUP NDR definitions, and loadparm context. This makes the header the coupling point for the LSA implementation.

## Risks and Edge Cases

- Field lifetime matters because state is shared across multiple files and sometimes cached beyond a single call.
- Adding fields increases coupling and should be paired with initialization in `dcesrv_lsa_get_policy_state()` or a documented lazy path.
- `enum lsa_handle` values must stay aligned with `dcesrv_handle_create()` and `DCESRV_PULL_HANDLE()` usage.

## Test Signals

Build coverage catches most header drift. Runtime validation comes from OpenPolicy, LookupNames/Sids, account, secret, and trusted-domain tests that exercise the fields initialized into `lsa_policy_state`.
