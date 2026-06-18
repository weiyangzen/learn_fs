# sources/sync-backup/git-lfs/t/t-install-custom-hooks-path.sh

## Purpose

Tests supported `core.hooksPath` handling during `git lfs install`, including normal custom paths, running install from a subdirectory, and shell-expanded `~` paths.

## Important APIs, control flow, and dependencies

The file requires Git 2.9+, defines `assert_hooks` and `refute_hooks`, initializes repos, sets `core.hooksPath`, runs `git lfs install`, and verifies `pre-push`, `post-checkout`, `post-commit`, and `post-merge` live in the configured hook directory rather than `.git` or a caller subdirectory.

## State, dependencies, integration points, risks, and test signals

State includes `.git/config`, custom hook directories, `$HOME/custom_hooks_dir`, and generated hook scripts. Integration points are hooksPath resolution, relative path behavior from subdirectories, tilde expansion, and hook installer coverage for all LFS hooks. Risks include writing to the wrong relative directory, leaving partial hooks, or failing to expand `~`. Signals are hook existence/refutation checks and `Updated Git hooks` grep.
