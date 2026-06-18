# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/newns.c

Command wrapper for constructing a new namespace and then execing a command. Supports `-a` to add namespace rules, `-d` for debug, and `-n namespace` to select the namespace file.

Defaults to `/lib/namespace` and `/bin/rc -i`. If exec of a relative command fails, it retries under `/bin`.
