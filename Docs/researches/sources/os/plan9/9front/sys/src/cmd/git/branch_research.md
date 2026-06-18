# File Research: sources/os/plan9/9front/sys/src/cmd/git/branch

rc script for listing, switching, creating, removing, and merging branches.

Key responsibilities:
- Lists local/remote branch refs or all branches from git/fs control state.
- Resolves target branch/base refs, including auto-creating local heads from origin refs.
- Prevents clobbering uncommitted changes unless merge/remove options allow it.
- Updates working tree files from the target branch tree and records index updates.
- Runs `merge1` for dirty paths requiring three-way merge.
- Updates `.git/HEAD` and target ref.

Important behavior:
- Ref names are normalized under `refs/heads/`.
- `-r` refuses to remove the current branch.
- `-s` updates branch ref without switching HEAD.

Notable risks:
- File/directory type transitions are handled by `rm -rf`, so path normalization must be correct.
