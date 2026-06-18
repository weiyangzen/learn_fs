# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/authsrv.c

Main Plan 9 authentication server request handler.

Key points:
- Reads fixed-size ticket requests and dispatches by request type.
- Supports ticket requests, challenge/response, password changes, APOP, CRAM, CHAP, MS-CHAP, HTTP passwords, and VNC.
- Issues encrypted tickets and authenticators using Plan 9 auth structures.
- Uses key databases `/mnt/keys` and `/mnt/netkeys`.
- Checks host/user delegation with `/lib/ndb/auth` `hostid` and `uid` entries.
- Implements LM/NT password hashes and MS-CHAP responses.
- Logs failures and optionally debug successes.

Dependencies:
- Uses `authsrv.h`, `libsec`, `ndb`, and shared auth command library.

Notable behavior:
- For unknown users/hosts, random keys are generated to avoid revealing account existence.
- VNC reverses bits in password bytes before DES use, matching VNC convention.
