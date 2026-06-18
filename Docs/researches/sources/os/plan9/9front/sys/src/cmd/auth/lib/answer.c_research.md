# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/answer.c

Interactive yes/no prompt helper for auth commands.

Key responsibilities:
- Prompts with `<question> [y/n]`.
- Returns true for `y` or `Y`; false otherwise.
- Frees the console response buffer.

Dependencies:
- Uses `readcons` from Plan 9 auth command environment.
