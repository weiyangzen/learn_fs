# File Research: sources/os/plan9/9front/sys/src/cmd/auth/none.c

Command wrapper that becomes user `none`, builds a namespace, and runs a command.

Key responsibilities:
- Supports `-n namespace` and `-d` namespace debug.
- Calls `procsetuser("none")`.
- Builds namespace for `none`.
- Defaults to interactive `/bin/rc -i`.
- Executes requested command, retrying relative command names under `/bin`.

Dependencies:
- Uses Plan 9 auth namespace helpers, `procsetuser`, and `newnsdebug`.
