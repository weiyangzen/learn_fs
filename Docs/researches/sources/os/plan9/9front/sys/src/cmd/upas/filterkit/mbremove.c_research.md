# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbremove.c

This command removes or truncates user mailboxes/folders without using upas/fs.

Key behavior:
- Usage: `mbremove [-fpqrtv] ...`.
- Default removes mailboxes; `-f` removes folders.
- `-r` recurses, `-t` truncates instead of deleting, `-p` prints/dry-runs removal effects, `-v` prints removed paths, `-q` redirects stderr to `/dev/null`.
- `idiotcheck` only allows directories, lock files, index files when appropriate, message files, or mbox-looking files to be removed.
- Removes `.idx` and `.imp` sidecars, or only truncates `.idx` during truncation.

Integration and risks:
- Contains its own `dirskip` and mbox detection logic, parallel to upas/fs `remove.c`.
- `isindex` condition uses `if(strcmp(p, ".idx") || strcmp(p, ".imp")) return 1;`, meaning it returns true for almost every suffix except impossible simultaneous equality; this mirrors code in `fs/remove.c` and looks suspicious.
