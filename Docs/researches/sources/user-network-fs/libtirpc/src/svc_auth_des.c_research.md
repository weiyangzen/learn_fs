<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_des.c -->
# sources/user-network-fs/libtirpc/src/svc_auth_des.c

Purpose: server-side AUTH_DES authenticator with conversation-key cache, timestamp replay protection, nickname support, and DES-to-Unix credential mapping.

Important APIs and functions: `_svcauth_des()` authenticates AUTH_DES credentials. Cache helpers `cache_init()`, `cache_victim()`, `cache_ref()`, `cache_spot()`, and `invalidate()` manage a 64-entry LRU cache. `authdes_getucred()` maps an authenticated network name to Unix uid/gid/groups and caches the result.

Control flow: full-name credentials parse the client netname, encrypted conversation key, and window; nickname credentials index an existing cache entry. The authenticator decrypts the timestamp using CBC for full credentials or ECB for nickname credentials, validates microseconds, replay ordering, and expiration window, builds an encrypted reply verifier using timestamp minus one second, then commits session data to the cache. Full-name credentials resolve a public key and decrypt the session key; nickname credentials hydrate full-name fields from the cache entry. Unix credential lookup calls `netname2user()` on cache miss.

State and persistence: process-global `authdes_cache`, `authdes_lru`, and `svcauthdes_stats` persist after lazy initialization. Each cache entry stores a session key, client name, window, last timestamp, and optional local credential cache. There is no explicit locking around this global cache in this file.

Dependencies and integration points: used from `svc_auth.c` when `AUTHDES_SUPPORT` is enabled. Depends on DES crypt routines, public-key lookup/decryption, netname-to-user mapping, RPC auth/des structs, and debug logging.

Risks: legacy DES cryptography is weak by modern standards. Global cache access appears unsynchronized. Direct IXDR parsing assumes valid opaque lengths supplied by the RPC message. Replay checks depend on system time and timestamp monotonicity. Some credential fields are stored in fixed-width short fields in local credential cache.

Test signals: full-name authentication with valid public key/session key, nickname reuse, replayed timestamp rejection, expired timestamp rejection, invalid microseconds, bad nickname, window verifier mismatch, DES encrypt/decrypt failure paths, LRU victim replacement, and `authdes_getucred()` success/unknown/cache-hit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/svc_auth_des.c -->
