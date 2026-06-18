# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/user.c

gefs `/adm/users` loader and parser.

Key responsibilities:
- Reads the users file from a snapshot tree through `Kdat` block pointers.
- Parses user records of the form `id:name:leader:members`.
- Builds `User` entries with ids, names, group leaders, and member id lists.
- Swaps the loaded user table under `fs->userlk`.
- Resolves users by id or name.

Important behavior:
- Parsing is two-pass: first ids/names, then leader and membership references.
- `loadusers()` falls back to a minimal default table only when no prior table exists and permissive mode is enabled.
- Updates global `noneid`, `admid`, and `nogroupid` after load.

Notable risks:
- `slurp()` does not drop blocks after `getblk()`, which appears to leak block references.
- User file size is capped at 1 MiB.
