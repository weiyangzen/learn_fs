## sources/user-network-fs/libtirpc/src/getpublickey.c

Purpose: Implements public-key lookup for AUTH_DES/Secure RPC from `/etc/publickey` with optional NIS fallback.

Important APIs and control flow: `getpublickey` dispatches to `__getpublickey_LOCAL` when set, otherwise `__getpublickey_real`. The real path calls `getpublicandprivatekey`, splits the returned `public:private` record at `:`, copies `HEXKEYBYTES` of public key, and terminates it. `getpublicandprivatekey` scans `/etc/publickey`, skipping comments, honoring `+` NIS inclusion when compiled with YP, parsing key/value fields with `strsep`, and copying the matched value to `ret`.

State and persistence: Global function pointer hook allows local server overrides. External state is `/etc/publickey` and optional NIS maps.

Dependencies and integration: Used by key/auth DES code and exported in newer map versions.

Risks and test signals: Uses `strcpy` into caller-provided buffers and assumes adequate size. Tests should cover local hook, missing file, malformed records, NIS-disabled `+`, exact key matching, public/private split, and buffer sizing.
