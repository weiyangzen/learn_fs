# sources/user-network-fs/samba/source3/rpc_client/init_lsa.h

## Purpose
`init_lsa.h` declares helper functions for initializing LSA string wrappers and encrypting trusted-domain auth info for LSA RPC clients.

## Important APIs, Types, And Functions
The header forward-declares generated LSA string types and declares `init_lsa_String()`, `init_lsa_StringLarge()`, `init_lsa_AsciiString()`, `init_lsa_AsciiStringLarge()`, `rpc_lsa_encrypt_trustdom_info()`, and `rpc_lsa_encrypt_trustdom_info_aes()`.

## Control Flow
There is no runtime logic. The prototypes define a caller contract: pass caller-owned strings and a session key, receive talloc-allocated internal auth info structures through output pointers.

## State And Persistence
The header carries no state. The declared encryption helpers produce transient RPC payloads rather than durable local persistence.

## Dependencies And Integration Points
It is consumed by rpcclient LSA command code and torture tests, and it depends on generated LSA auth-info structures being visible to the including translation unit.

## Risks
The API exposes nullable `const char *` parameters but the implementation expects valid strings. Callers need to validate inputs before invoking it. Return type is `bool`, limiting diagnostics.

## Test Signals
Build coverage catches generated type/signature drift. Behavioral coverage belongs with `init_lsa.c`: trust-domain password set/query flows, AES and RC4 compatibility, and failure handling for allocation/conversion errors.
