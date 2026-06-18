# sources/sync-backup/git-lfs/t/t-batch-storage-corrupt.sh

## Purpose
Verifies that Git LFS detects corrupted object data during download and does not persist invalid content or advance Git state incorrectly. It covers HTTP, pure SSH transfer, and custom transfer adapter paths.

## Important APIs, Functions, and Control Flow
Each test commits an LFS object, pushes it, removes local object data, causes the remote or test server to serve inverted-case corrupt content, then runs `git lfs pull` and `git pull`. The script asserts failed hash validation, absence of both expected and corrupt objects from local storage, appropriate `git lfs fsck` behavior, and that `HEAD` remains unchanged after smudge errors during `git pull`.

## State, Persistence, and Dependencies
State includes local object caches, remote LFS object files, worktree files, `initial_sha`, and logs. Dependencies include `setup_pure_ssh`, `ssh_remote`, custom adapter `lfstest-customadapter`, `invert_case`, `calc_oid`, `assert_server_object`, `assert_remote_object`, and `git lfs fsck`.

## Integration Points, Risks, and Test Signals
The tests exercise HTTP transfer, pure SSH `git-lfs-transfer`, and custom adapter integrity checks. Signals are expected/got OID messages, `downloaded file failed checks`, `Smudge error`, `Failed to fetch some objects`, and `Git LFS fsck OK` after resetting. Risks include exact log matching and platform-specific remote object path handling.
