# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/none.c

Runs a command as user `none` in a new environment/name group. It writes `none` to `#c/user`, builds a namespace for `none`, then execs the requested command or `/bin/rc`.

Useful for dropping privilege into the conventional unauthenticated Plan 9 user.
