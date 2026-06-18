# File Research: sources/os/plan9/plan9/sys/src/9/boot/doauthenticate.c

Legacy boot authentication/session helper.

Key behavior:
- `readn()` reads an exact byte count or fails.
- `fromauth()` connects to method auth server, sends ticket request, and reads ticket or error response.
- `doauthenticate()` performs `fsession()`, obtains a ticket, and calls `fauth()`; if auth server is unavailable or auth fails, it prints a warning and falls back.
- `checkkey()` validates a user/key pair by requesting and decrypting a ticket.

The current `boot.c` primarily uses factotum-based `authentication()`, but these helpers remain for method-level auth flows.
