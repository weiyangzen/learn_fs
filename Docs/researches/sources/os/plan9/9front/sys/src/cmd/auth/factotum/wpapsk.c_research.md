# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/wpapsk.c

Factotum WPA-PSK pairwise transient key generator.

Key responsibilities:
- Supports client role only; server role is unimplemented.
- Accepts binary challenge: supplicant MAC, authenticator MAC, supplicant nonce, authenticator nonce.
- Finds a key with `essid` and private `!password`.
- Converts password to PMK either from 64 hex chars or PBKDF2-HMAC-SHA1 over ESSID.
- Computes WPA pairwise key expansion PRF to produce a 64-byte PTK.
- Returns the PTK on read.

Dependencies:
- Uses factotum key lookup, PBKDF2, HMAC-SHA1, and WPA key derivation conventions.

Notable risks:
- Challenge size must exactly match 2 MAC addresses plus 2 nonces.
