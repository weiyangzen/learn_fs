# sources/sync-backup/git-lfs/t/t-cherry-pick-commits.sh

## Purpose
Tests that cherry-picking multiple LFS-containing commits succeeds when the local LFS object cache has been removed. This exercises smudge/download behavior during Git cherry-pick.

## Important APIs, Functions, and Control Flow
The test creates a remote, tracks `*.dat`, makes an initial commit, creates `secondbranch`, commits `a.dat` and `b.dat` on main, records both commit IDs, pushes main, checks out `secondbranch`, deletes `.git/lfs/objects`, and runs `git cherry-pick $commit1 $commit2`.

## State, Persistence, and Dependencies
State includes branch topology, two LFS commits, remote uploaded LFS objects, and an intentionally empty local LFS object cache. It depends on `setup_remote_repo`, `clone_repo`, and normal Git LFS smudge/filter integration.

## Integration Points, Risks, and Test Signals
The integration point is Git invoking LFS filters while applying cherry-picked commits. The test signal is command success under `set -e`; there are no explicit content assertions after cherry-pick. The main risk is low diagnostic specificity if cherry-pick succeeds but content is wrong.
