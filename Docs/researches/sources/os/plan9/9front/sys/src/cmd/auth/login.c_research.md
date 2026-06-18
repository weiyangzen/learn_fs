# File Research: sources/os/plan9/9front/sys/src/cmd/auth/login.c

Interactive local login command that authenticates a user and starts an rc session.

Key responsibilities:
- Prompts for a user's password and authenticates with `auth_userpasswd`.
- Consumes the returned uid-change capability through `/dev/capuse`.
- Starts a fresh factotum instance and loads `dp9ik` and `p9sk1` password keys into it.
- Builds the authenticated user's namespace with `newns`.
- Re-mounts the new factotum into the namespace and removes the temporary srv file.
- Rebuilds a clean environment with user, home, service, cputype, sysname, and timezone.
- Changes to `/usr/<user>` or `/`, then execs interactive login rc.

Dependencies:
- Uses Plan 9 auth library, `/boot/factotum`, `/srv`, `/mnt/factotum/ctl`, `/dev/capuse`, ndb/csipinfo authdom lookup, and `newns`.

Notable risks:
- Warns if run on a CPU server.
- Password is passed to the child factotum through its control file, then cleared locally.
