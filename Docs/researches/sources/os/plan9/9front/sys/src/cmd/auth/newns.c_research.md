# File Research: sources/os/plan9/9front/sys/src/cmd/auth/newns.c

Command wrapper that builds or extends the current user's namespace before running a command.

Key responsibilities:
- Supports `-n namespace`, `-d` namespace debug, and `-a` additive namespace mode.
- Calls `newns(getuser(), namespace)` or `addns(getuser(), namespace)` in a fresh name group.
- Defaults to interactive `/bin/rc -i`.
- Executes requested command, retrying relative command names under `/bin`.

Dependencies:
- Uses Plan 9 auth namespace helpers and `newnsdebug`.
