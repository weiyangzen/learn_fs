# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/secchk.c

Small SecureID check test command for secstore/auth configuration.

Key responsibilities:
- Opens `/lib/ndb/auth` and local ndb, concatenating them for lookup.
- Prints current user.
- Calls `secureidcheck(getenv("user"), argv[1])` and prints the result.

Dependencies:
- Uses ndb and external `secureidcheck`.

Research notes:
- Usage string says the single argument is `pinsecurid`.
