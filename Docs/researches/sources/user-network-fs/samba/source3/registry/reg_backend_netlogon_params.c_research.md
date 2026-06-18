# sources/user-network-fs/samba/source3/registry/reg_backend_netlogon_params.c

## Purpose

`reg_backend_netlogon_params.c` implements a dynamic registry backend for Netlogon parameters. It exposes the Samba account policy controlling machine password change refusal as a registry DWORD.

## Important APIs, Types, and Functions

- `netlogon_params_fetch_values()` reads `PDB_POLICY_REFUSE_MACHINE_PW_CHANGE` and adds `RefusePasswordChange`.
- `netlogon_params_fetch_subkeys()` delegates to `regdb_ops`.
- `netlogon_params_reg_ops` publishes the backend operations table.

## Control Flow

On value fetch, the backend asks passdb for `PDB_POLICY_REFUSE_MACHINE_PW_CHANGE`; if unavailable, it defaults to `0`. It then adds a `REG_DWORD` value named `RefusePasswordChange` and returns the value count. Subkey fetches are delegated to the persistent DB backend.

## State and Persistence

The exposed value is dynamic and derived from passdb account policy. This backend does not store registry values itself.

## Dependencies and Integration Points

It depends on passdb policy APIs, registry containers, and default `regdb_ops`. It integrates with registry hook dispatch for `KEY_NETLOGON_PARAMS`.

## Risks and Edge Cases

- Failure to read the account policy is indistinguishable from an explicit zero value to registry callers.
- Only fetch operations are defined; mutations must be handled elsewhere or rejected.

## Test Signals

Tests should mock or set account policy to both 0 and 1, verify default 0 on policy read failure, confirm value type/size/name, and verify subkey delegation.
