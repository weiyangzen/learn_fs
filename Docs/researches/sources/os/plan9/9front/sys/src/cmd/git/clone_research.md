# File Research: sources/os/plan9/9front/sys/src/cmd/git/clone

rc script for cloning remote repositories with 9front git.

Key responsibilities:
- Creates `.git` layout, writes origin remote config, fetches remote refs through `git/get`, and sets local HEAD.
- Selects default branch from remote HEAD/symref or requested `-b` branch.
- Checks out the selected branch through `git/fs` and tar-copy from the mounted tree.
- Seeds `.git/INDEX9` with tracked tree entries.
- Cleans partially cloned destination on interrupt or failure.

Important behavior:
- Local directory defaults to the remote basename without `.git`.
- Empty existing destination is allowed; non-empty destination is rejected.
- Remote heads are stored under `.git/refs/remotes/origin`.

Notable risks:
- The checkout path relies on `.git/fs/HEAD/tree` after starting `git/fs`.
