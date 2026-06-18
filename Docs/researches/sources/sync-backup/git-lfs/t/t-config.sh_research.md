# sources/sync-backup/git-lfs/t/t-config.sh

## Purpose
Tests Git LFS configuration discovery, precedence, URL rewriting, extension configuration, safe `.lfsconfig` handling, and include directives under `GIT_CONFIG`.

## Important APIs, Functions, and Control Flow
Tests inspect `git lfs env` and `git lfs ext` output under combinations of remote URL defaults, `.lfsconfig`, local/global Git config, repository-tree `.lfsconfig` via `HEAD` and index, extension config precedence, `url.*.insteadOf` longest-match and ambiguity behavior, unsafe key filtering, and included config files. One test ensures an LFS-tracked file named before `.lfsconfig` lexicographically does not prevent config loading during clone.

## State, Persistence, and Dependencies
State includes `.lfsconfig`, `.git/config`, global config, included config files, remote refs, and LFS object caches. Dependencies include `setup_remote_repo`, `git lfs env`, `git lfs ext`, URL alias logic, and Git config include support.

## Integration Points, Risks, and Test Signals
Integration points are endpoint discovery, auth access mode selection, extension loading, Git URL rewriting, repository config loading from tree/index, and `.lfsconfig` safety filtering. Signals are exact `Endpoint=... (auth=...)`, `Extension: ...`, warning text, and cloned file contents. Risks are exact output wording and global config side effects.
