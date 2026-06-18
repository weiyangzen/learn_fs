# File Research: sources/os/plan9/9front/sys/src/cmd/auth/changeuser.c

Interactive user account/key installer for Plan 9 and Securenet authentication databases.

Key responsibilities:
- Selects Plan 9 (`-p`) and/or Securenet (`-n`) account updates; defaults to Plan 9.
- Validates username length.
- Prompts whether to assign new Plan 9 password and optional Inferno/POP secret.
- Preserves existing expiration time and writes key/secret updates.
- Queries and writes account bio records.
- For Securenet, generates a random DES key, writes it, prints the key and checksum for verification.
- Logs account installation through auth syslog.

Dependencies:
- Uses helpers from `authcmdlib.h`, including key database access, password prompting, account bio I/O, and DES key formatting.

Research notes:
- `install()` creates user directories when absent and writes expiration if present.
- The command intentionally calls `private()` before modifying auth state.
