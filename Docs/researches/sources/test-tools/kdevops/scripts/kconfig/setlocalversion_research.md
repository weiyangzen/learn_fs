# sources/test-tools/kdevops/scripts/kconfig/setlocalversion

## Purpose
`setlocalversion` emits a version suffix derived from the current source control state. This copy is derived from Linux kernel tooling and simplified for kdevops/Coccinelle-style trees.

## Important APIs, Types, And Functions
The main shell function is `scm_version()`. Global variables include `TAGS="--tags"`, `srctree=.`, and accumulated `res`. Git handling uses `git rev-parse`, `git describe`, `git diff-index`, and `awk`; Mercurial handling uses `hg id` and `hg log`.

## Control Flow
`scm_version()` first checks for a Git repository at the root. If HEAD is not exactly at a tag, it emits a formatted distance/hash from `git describe --tags` or `-g<hash>` if no tag exists. It appends `-dirty` when tracked changes exist outside `scripts/package`. If not Git, it checks Mercurial, emits tag or changeset suffixes, and appends `-dirty` for modified state. The script prints the resulting suffix.

## State And Persistence
No files are written. Output depends on repository tags, current HEAD, VCS metadata, and dirty working-tree state.

## Dependencies And Integration Points
Depends on `/bin/sh`, Git and/or Mercurial, `awk`, `cut`, and `sed`. Build systems can call it to embed local version suffixes into generated metadata.

## Risks And Edge Cases
The script uses `--tags`, so lightweight tags affect version selection. Dirty detection ignores only `scripts/package` and may be noisy in this repository. Mercurial branch uses `==` in `/bin/sh`, which is not portable to all shells. Repositories with no tags fall back to a hash suffix.

## Test Signals
Run in clean tagged Git, clean commits after a tag, dirty Git, tagless Git, outside a repository, and Mercurial if supported. Verify exact suffix formatting.
