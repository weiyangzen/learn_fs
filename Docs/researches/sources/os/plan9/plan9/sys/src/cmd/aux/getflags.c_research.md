# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/getflags.c

This file parses command flags according to the `flagfmt` environment variable and emits rc assignments.

Key behavior:
- Reads `$flagfmt`.
- Initializes all declared `flagX=()` variables.
- Parses command-line flags with Plan 9 `ARGBEGIN`.
- Emits scalar `flagX=1` for boolean flags and list assignments for flags with arguments.
- Emits remaining positional arguments as `*=()` and clears `status`.

Important details:
- Uses rc-compatible quoting through `quotefmtinstall`.
- Prints `status=usage` on usage and `exit 'missing flagfmt'` if the environment is absent.

Filesystem relevance:
- Indirect shell utility; no filesystem implementation logic.
