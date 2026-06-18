# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libauth/auth_proxy.c

This file proxies an authentication protocol between a connection and an `AuthRpc`.

Key behavior:
- `auth_proxy` opens `/mnt/factotum/rpc`, starts an RPC, and delegates to `fauth_proxy`.
- `fauth_proxy` loops over RPC states, reading/writing protocol bytes on the supplied fd.
- `auth_getinfo` retrieves and decodes final `AuthInfo`.
- `auth_freeAI` releases decoded auth info.
- `convM2AI`, `gstring`, and `gcarray` decode factotum's packed auth-info reply.

Important details:
- Handles `ARdone`, `ARok`, `ARphase`, `ARneedkey`, `ARtoosmall`, and error states.
- Returns peer credential data including `cuid`, `suid`, capability, secret, and auth domain.
