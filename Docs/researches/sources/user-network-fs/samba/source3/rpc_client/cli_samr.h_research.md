# sources/user-network-fs/samba/source3/rpc_client/cli_samr.h research

## Purpose

`cli_samr.h` declares source3 SAMR convenience routines implemented in `cli_samr.c`. It provides both `dcerpc_binding_handle`-based APIs and `rpc_pipe_client` wrappers for password changes, plus helper declarations for QueryDisplayInfo sizing and compatible SAMR connect attempts.

## Important APIs, types, and functions

The header exposes `dcerpc_samr_chgpasswd_user()`, `rpccli_samr_chgpasswd_user()`, `dcerpc_samr_chgpasswd_user2()`, `rpccli_samr_chgpasswd_user2()`, `dcerpc_samr_chng_pswd_auth_crap()`, `rpccli_samr_chng_pswd_auth_crap()`, `dcerpc_samr_chgpasswd_user3()`, `rpccli_samr_chgpasswd_user3()`, and `dcerpc_samr_chgpasswd_user4()`. It also exposes `dcerpc_get_query_dispinfo_params()` and `dcerpc_try_samr_connects()`.

The declarations reference generated SAMR types such as `policy_handle`, `samr_DomInfo1`, and `userPwdChangeFailureInformation`, plus Samba `DATA_BLOB`, `NTSTATUS`, `TALLOC_CTX`, and `rpc_pipe_client`.

## Control flow and contracts

The `dcerpc_` functions accept an already-bound `struct dcerpc_binding_handle *h`; they return transport/call NTSTATUS and write the server-side SAMR result to `presult`. The `rpccli_` functions accept an already-bound `struct rpc_pipe_client *cli` and collapse the two-status pattern by returning the server result when transport succeeded.

Password-change variants differ in addressing and encoding: handle-based `ChangePasswordUser`, username/server-name based `ChangePasswordUser2`, blob-based ChangePasswordUser2, `ChangePasswordUser3` with policy feedback outputs, and AES `ChangePasswordUser4`.

## State and persistence behavior

The header exposes no global state. Output structures are caller-owned through `mem_ctx`, and callers are responsible for valid bound handles and policy handles. Server-name strings in `rpccli_` wrappers are supplied from `rpc_pipe_client->srv_name_slash`.

## Dependencies and integration points

This header is consumed by account/password tools and domain code that need SAMR password operations without duplicating crypto marshalling. It sits above generated NDR SAMR stubs and below user-facing utilities.

## Risks and test signals

Because the prototypes expose plaintext password parameters, callers must control lifetimes and logging. Tests should verify both direct `dcerpc_` and `rpccli_` APIs, ensure `presult` is initialized on failures as expected by callers, and compile-check all declared functions against generated SAMR type definitions.
