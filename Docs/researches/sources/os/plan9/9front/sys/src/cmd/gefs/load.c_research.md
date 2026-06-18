# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/load.c

gefs mount-time loader for superblocks, arenas, allocation logs, and users.

Key responsibilities:
- Loads arena header/footer pairs, accepting either valid copy as fallback.
- Initializes arena free-range AVL trees, log buffers, and cache-plucked static blocks.
- Loads primary superblock, falling back to the backup superblock at device end.
- Reconstructs arena free state by replaying allocation logs.
- Opens the `adm` snapshot and loads `/users`.

Important behavior:
- `loadfs()` creates a synthetic `dump` mount rooted at `fs->snap`.
- Arena reserve is derived from arena size and clamped between 512 KiB and 8 MiB.
- Prints loaded filesystem geometry and generation/qid state.

Notable risks:
- The fallback message for backup superblock says “primary” twice.
- If both arena header copies fail, loading aborts with `Efs`.
