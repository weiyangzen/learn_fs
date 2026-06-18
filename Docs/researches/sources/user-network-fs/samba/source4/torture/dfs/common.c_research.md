# sources/user-network-fs/samba/source4/torture/dfs/common.c

## Purpose
This file provides the shared DFS referral transaction helper used by the DFS torture tests.

## Important APIs, types, and functions
The only exported function is `dfs_cli_do_call(struct smbcli_tree *tree, struct dfs_GetDFSReferral *ref)`. It uses `struct smb_trans2`, setup code `TRANSACT2_GET_DFS_REFERRAL`, `ndr_push_struct_blob()`, `ndr_pull_struct_blob()`, generated NDR routines `ndr_push_dfs_GetDFSReferral_in` and `ndr_pull_dfs_referral_resp`, and `smb_raw_trans2()`.

## Control flow
The function initializes a TRANS2 request with one setup word, marshals `ref->in.req` into the parameter blob, sends the request, and unmarshals `trans.out.data` into `ref->out.resp`. Push failures return `NT_STATUS_INTERNAL_ERROR`, transport/server failures are returned directly, and pull failures return `NT_STATUS_INVALID_NETWORK_RESPONSE`.

## State and persistence
The helper is stateless aside from talloc allocations under `tree` for blobs. It does not create files or mutate share contents.

## Dependencies and integration points
It is the integration point between Samba's raw TRANS2 client and generated DFS referral NDR structures. Callers must initialize `ref->in.req.max_referral_level`, `ref->in.req.servername`, and `ref->out.resp`.

## Risks
The response buffer limit is fixed at 4096 bytes; unusually large referral responses may truncate or fail. The helper assumes response data, not params, contains the referral response. Memory is tied to `tree`, which is fine for test lifetime but can accumulate in long loops.

## Test signals
Signals are the exact NTSTATUS returned by `dfs_cli_do_call()` and whether response unmarshalling succeeds. `NT_STATUS_INVALID_NETWORK_RESPONSE` indicates malformed or incompatible DFS referral encoding.
