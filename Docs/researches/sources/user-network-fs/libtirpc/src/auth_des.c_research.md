<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_des.c -->
# sources/user-network-fs/libtirpc/src/auth_des.c

Purpose: Client-side AUTH_DES implementation for Secure RPC using DES-encrypted timestamp credentials.

Important APIs, types, and functions: Exports `authdes_seccreate` and `authdes_pk_seccreate`; implements auth ops `authdes_marshal`, `authdes_validate`, `authdes_refresh`, `authdes_destroy`, wrapping passthrough, and static op-vector initialization. Private state lives in `struct ad_private`.

Control flow: Creation resolves or accepts the server public key, gets the client netname, allocates private fields, creates or accepts a conversation key, sets AUTH_DES ops, then refreshes credentials. Marshal timestamps, applies time offset, encrypts timestamp/window, writes credential/verifier XDR. Validate decrypts server verifier and switches to nickname credentials. Refresh optionally syncs time and encrypts the session key with the server public key.

State and persistence behavior: Persistent per-AUTH state includes names, server key, conversation key, nickname, credential/verifier structs, time sync cache, and optional timehost endpoint strings. Destroy frees allocated private fields and AUTH.

Dependencies and integration points: Depends on keyserv/publickey APIs, DES crypt functions, XDR authdes coders, `__rpc_get_time_offset`, syslog/debug, and libtirpc auth ops locks. Built only when AUTH_DES is enabled.

Risks: AUTH_DES is legacy cryptography. Public key copy into fixed 1024-byte buffer lacks explicit length cap. Time synchronization and nickname state are subtle and can fail open by disabling sync. Error paths must avoid leaks across many allocated fields.

Test signals: No direct unit test in this subset; compile coverage when AUTH_DES is enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/auth_des.c -->
