# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/util.c

Shared factotum utility layer for auth dialing, key lookup, capabilities, authinfo serialization, and attribute handling.

Key responsibilities:
- Dials auth servers via normal `/net/cs` lookup or bootstrap `authaddr`/`/net/ndb` fallback.
- Performs auth-server request setup, including PAK key negotiation when AES key material exists.
- Prompts users for missing keys and writes them to `/mnt/factotum/ctl`.
- Implements key confirmation tracking and reference-counted key cleanup.
- Serializes `AuthInfo` into the factotum RPC wire format.
- Implements `failure`, `toosmall`, phase naming, and phase-error helpers.
- Searches the keyring with attribute patterns, owner restrictions, disabled-key filtering, confirmation checks, and needkey generation.
- Finds Plan 9 server auth keys, preferring `dp9ik` then `p9sk1`.
- Imports NVRAM keys into the factotum keyring.
- Creates uid-change capabilities through `/dev/caphash`.
- Replaces/adds keys in the keyring, copies/sets/sorts attributes, writes hostowner, and disables bad keys.

Dependencies:
- Uses Plan 9 networking, authsrv, NVRAM, factotum key structures, attr parser/formatter, HMAC-SHA1, and `/dev/hostowner`.

Notable risks:
- Key matching semantics combine requested attributes, protocol prompts, owner restrictions, and private attrs.
- Needkey prompts intentionally remove ignored attrs such as `role` and `disabled`.
