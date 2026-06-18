# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/login.c

Implements a console login program. It prompts for a password, authenticates via `auth_userpasswd`, writes the returned capability to `#¤/capuse` to change uid, starts a private factotum, seeds it with a `p9sk1` password key, builds the user namespace, and starts interactive `rc`.

It preserves selected environment variables (`cputype`, `sysname`, `timezone`) while creating a fresh environment with `service=con`, `user`, `home`, and object type. It warns when run on a CPU server.

Contains local copies of `readln`, `setenv`, factotum mount/start helpers, and uid-change logic.
