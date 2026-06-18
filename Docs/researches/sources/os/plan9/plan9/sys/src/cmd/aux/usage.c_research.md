# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/usage.c

Generic usage-message generator driven by environment variables.

Core behavior:
- Reads `$0`, `$flagfmt`, and `$args`.
- Prints `usage: <argv0> ...` to stderr.
- Parses `flagfmt` where single-character comma-separated flags can be grouped as `[-abc]`, while flags with arguments are printed as `[-x arg]`.
- Appends `$args`.
- Exits with status `usage`.

Dependencies and integration:
- Standalone Plan 9 libc utility.
- Designed for shell scripts or command wrappers that set `flagfmt`/`args`.

Notable risks:
- Mutates the `flagfmt` string returned by `getenv()` while parsing.
- Assumes `$0` exists; exits separately if missing.
