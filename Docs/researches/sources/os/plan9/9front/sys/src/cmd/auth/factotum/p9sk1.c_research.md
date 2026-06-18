# File Research: sources/os/plan9/9front/sys/src/cmd/auth/factotum/p9sk1.c

Factotum implementation of Plan 9 `p9sk1` and `dp9ik` authentication.

Key responsibilities:
- Implements client, server, and login-style state machines for Plan 9 secret-key authentication.
- Handles challenge exchange, ticket requests, tickets, authenticators, and final `AuthInfo`.
- Adds `dp9ik` PAK exchange to protect password-derived keys from offline dictionary attacks.
- Supports speak-for keys and client keys with owner/sysuser restrictions.
- Requests tickets from authsrv and falls back to locally generated tickets when authid and hostid match.
- Derives session secrets: DES-derived secret for `p9sk1`, HKDF-expanded secret for `dp9ik`.
- Parses keys from `!hex` or `!password`, hashes AES keys for PAK, and stores parsed `Authkey` in key private state.
- Disables never-successful bad client keys after failed ticket decryption where applicable.

Dependencies:
- Uses authsrv ticket/authenticator encoders, PAK helpers, HKDF/HMAC/SHA-256, DES key conversion, factotum keyring, capability-independent authinfo support.

Notable risks:
- This is the core Plan 9 authentication mechanism; phase ordering and ticket challenge checks are security-critical.
- Local ticket fallback is intentionally constrained to matching authid/hostid.
