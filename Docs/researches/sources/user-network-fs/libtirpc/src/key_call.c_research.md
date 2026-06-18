## sources/user-network-fs/libtirpc/src/key_call.c

Purpose: Implements Secure RPC keyserver client functions for setting secrets, encrypting/decrypting session keys, generating DES keys, storing netname key material, checking secret-key presence, and deriving conversation keys.

Important APIs and control flow: Public wrappers build `key_prot` argument/result structs and call the internal `key_call`. `key_call` first honors local override hooks for keyserver-internal AUTH_DES recursion, chooses keyserver protocol version 1 or 2 by procedure, obtains a cached loopback client from `getkeyserv_handle`, and performs `clnt_call` with a 30-second timeout. `getkeyserv_handle` keeps a thread-specific client, rebuilds after fork or effective uid change, searches loopback netconfig entries preferring `NC_TPI_COTS_ORD`, sets AUTH_SYS credentials for the effective uid, sets retry timeout, and marks the fd close-on-exec.

State and persistence: Thread-specific `key_call_private` caches a client by pid and euid. Global function pointers provide local implementations for keyserver use.

Dependencies and integration: Depends on netconfig, uname nodename, authsys, key_prot XDR, and client generic APIs.

Risks and test signals: Secret material is copied through stack/result structs; `key_secretkey_is_set` explicitly wipes the private key field. Tests should cover uid/pid cache invalidation, local hook dispatch, version selection, loopback fallback, auth recreation, and status-to-return mapping.
