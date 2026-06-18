# sources/user-network-fs/samba/source3/utils/net_rpc_rights.c

## Purpose

`net_rpc_rights.c` implements user-rights management for `net rpc rights` and exposes the same operations inside `net rpc shell`. It lists available LSA privileges, lists privileges assigned to accounts, lists accounts with a specific privilege, and grants or revokes rights for a name or raw SID.

## Important APIs, Types, and Functions

The file is centered on LSA RPC. `sid_to_name()` opens an LSA policy and calls `rpccli_lsa_lookup_sids()` for display. `name_to_sid()` accepts raw SID strings via `dom_sid_parse()` or resolves names with `rpccli_lsa_lookup_names()`. `enum_privileges()` calls `dcerpc_lsa_EnumPrivs()` and `LookupPrivDisplayName` to show available rights with descriptions. `enum_privileges_for_user()` and `check_privilege_for_user()` call `EnumAccountRights`; `enum_accounts_for_privilege()` and `enum_privileges_for_accounts()` enumerate account SIDs and join them with right membership.

`rpc_rights_list_internal()`, `rpc_rights_grant_internal()`, and `rpc_rights_revoke_internal()` implement the command behavior. The shell adapters `rpc_sh_rights_list()`, `rpc_sh_rights_grant()`, and `rpc_sh_rights_revoke()` reuse the same internals with the active shell context. `net_rpc_rights_cmds()` returns the nested shell command table.

## Control Flow

The standalone wrappers validate display-usage mode and call `run_rpc_command()` with `ndr_table_lsarpc`. Listing opens a policy once, then dispatches based on the first argument: no arguments or `privileges` without names lists all available privileges; `privileges <right...>` lists accounts that have each right; `accounts` without names lists every privileged SID and its rights; `accounts <name|SID...>` lists rights for each account; a single legacy argument is treated as an account name. Grant and revoke resolve the target SID, open an LSA policy with fallback support and maximum access, build an `lsa_RightSet` from the remaining arguments, then call `AddAccountRights` or `RemoveAccountRights`.

## State and Persistence

The persistent state is the target domain/server LSA account-right assignment database. Grant and revoke mutate rights for the resolved SID. Listing commands are read-only. Transient state includes policy handles, SID/name arrays, `lsa_RightSet` arrays, and talloc-backed display strings.

## Dependencies and Integration Points

This file depends on generated LSA RPC stubs, `rpc_client/cli_lsarpc.h`, `init_lsa.h`, security SID utilities, and Samba's command and shell frameworks. It integrates both as a standalone `net rpc rights` command and as the `rights` subtree in `net_rpc_shell.c`.

## Risks

Most operations request `SEC_FLAG_MAXIMUM_ALLOWED`, so failures depend heavily on remote privilege and policy configuration. `enum_accounts_for_privilege()` enumerates all accounts and then calls `EnumAccountRights` for each, which can be expensive on large domains. List mode often continues after privilege lookup errors and returns the last status, which may not reflect partial failures clearly. Grant/revoke accept arbitrary right strings and rely on server-side validation. Some close calls run even when policy open failed, though invalid handles are usually tolerated by Samba helpers.

## Test Signals

Useful tests include raw SID parsing, name resolution failure mapping, listing all privileges on a known server, granting and revoking a test privilege to a disposable account, shell command reuse, and behavior when the caller lacks rights. A scale test for `rights list privileges <right>` should cover domains with many account SIDs.
