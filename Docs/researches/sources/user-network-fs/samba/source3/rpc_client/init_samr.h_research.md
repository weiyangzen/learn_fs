# sources/user-network-fs/samba/source3/rpc_client/init_samr.h

## Purpose
`init_samr.h` declares SAMR password encryption buffer initializers used by RPC client and account-management code.

## Important APIs, Types, And Functions
It declares `init_samr_CryptPasswordEx()`, `init_samr_CryptPassword()`, and `init_samr_CryptPasswordAES()`. Inputs are cleartext password strings, session keys, and for AES a salt plus talloc context; outputs are generated SAMR encrypted password structures.

## Control Flow
There is no runtime control flow. The header's contract separates legacy RC4 formats from the AES encrypted password format.

## State And Persistence
No state is held in the header. The implementation creates transient encrypted RPC payloads only.

## Dependencies And Integration Points
The declarations are consumed by rpcclient SAMR commands, domain join/password-change code, NetAPI user management, source4 password tooling, and SAMR torture tests. Including code must have generated SAMR and Samba base types available.

## Risks
Callers must supply valid session keys and salt sizes. The API does not encode ownership details beyond the AES `mem_ctx`, so callers must understand which output buffers are talloc-owned.

## Test Signals
Compile tests catch signature drift. Runtime coverage comes from password set/change RPC paths, AES password buffer tests, and negative tests for invalid parameters.
