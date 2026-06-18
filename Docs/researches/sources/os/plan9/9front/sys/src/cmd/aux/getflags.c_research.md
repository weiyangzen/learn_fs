# File Research: sources/os/plan9/9front/sys/src/cmd/aux/getflags.c

Role: Helper that parses command-line flags according to `$flagfmt` and emits rc-compatible variable assignments.

Flag format:
- Reads `flagfmt` from the environment.
- Each flag spec can be a rune flag or `r:name` style named flag; whitespace after a spec indicates that the flag takes arguments.
- Comma separates flag specifications.

Output:
- Initializes each flag variable to `()`.
- Prints `flagX=1` or `name=1` for boolean flags.
- Prints list assignments for flags with arguments.
- Prints `*=()` containing remaining positional arguments and `status=''` on success.
- On usage errors prints `status=usage`.

Implementation:
- Uses Plan 9 `ARGBEGIN` and rune-aware parsing (`chartorune`, `runelen`), so non-ASCII option names can be parsed.
