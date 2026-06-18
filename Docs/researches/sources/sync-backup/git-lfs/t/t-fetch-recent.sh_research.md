# sources/sync-backup/git-lfs/t/t-fetch-recent.sh

## Purpose

Tests recent-object fetching policy. It builds a repository with commits and branches at controlled dates, then verifies `git lfs fetch` behavior for `lfs.fetchrecentalways`, recent refs days, recent commits days, older commits, remote branches, and remote refs.

## Important APIs, control flow, and dependencies

The setup uses `lfstest-testutils addcommits` with dates from `get_date`, creates `main` and `other_branch`, pushes both, and clones a test repo. Follow-up tests mutate fetch-recent config values, delete `.git/lfs/objects`, call `git lfs fetch`, and assert which of `oid0` through `oid5` appear locally.

## State, dependencies, integration points, risks, and test signals

State includes commit timestamps, branch reachability, remote refs, LFS objects, and fetch-recent config. Integration points are revision scanning, time-window calculations, remote ref inclusion, branch checkout state, and object download scheduling. Risks include off-by-one day windows, local time variance, missing remote-only refs, or downloading old unreachable objects. Signals are object presence/absence assertions per scenario.
