# sources/user-network-fs/samba/source3/rpcclient/cmd_dssetup.c

## Purpose
`cmd_dssetup.c` provides a single `rpcclient` command for querying primary domain role information through the DSSETUP RPC interface.

## Important APIs, types, and functions
- `cmd_ds_dsrole_getprimarydominfo()` calls `dcerpc_dssetup_DsRoleGetPrimaryDomainInformation()` with `DS_ROLE_BASIC_INFORMATION`.
- It prints the machine role and whether Directory Service is running, including mixed/native mode when applicable.
- `ds_commands[]` registers the `LSARPC-DS` command group and `dsroledominfo` command as `RPC_RTYPE_WERROR` against `ndr_table_dssetup`.

## Control flow
The command sends the DS role query through `cli->binding_handle`, converts transport errors to `WERROR`, returns server-side `werr` failures directly, and prints fields from `info.basic` on success.

## State and persistence behavior
The command is read-only and maintains no local or remote persistent state.

## Dependencies and integration points
The file depends on `rpcclient.h` and generated DSSETUP client stubs. It is part of rpcclient's LSARPC/DS administrative command surface.

## Risks and edge cases
- There is no explicit argument count validation, so extra arguments are ignored.
- Output is intentionally sparse and only covers the basic information level.
- Correctness depends on generated union layout for `union dssetup_DsRoleInfo`.

## Test signals
Run `dsroledominfo` against member servers, standalone servers, and AD DCs to verify role, DS-running, and mixed/native output. Negative tests should include denied credentials or unavailable DSSETUP.
