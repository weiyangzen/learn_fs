# sources/sync-backup/git-lfs/t/t-batch-transfer.sh

## Purpose
Broad integration coverage for batch transfers over HTTP and SSH. It verifies basic push/pull, object ordering, hash algorithm handling, legacy SSH authentication, pure SSH transfer sessions, multiplexing, concurrency limits, and multi-branch fetches.

## Important APIs, Functions, and Control Flow
The script begins with `setup_expected_concurrent_transfers`. Tests create repositories, track `*.dat`, commit objects, push, clone/fetch/pull, and assert object presence. `assert_ssh_transfer_session_counts` and `assert_ssh_transfer_sessions` parse trace logs to validate `git-lfs-transfer` control and non-control SSH sessions, including special handling for older Git smudge behavior.

## State, Persistence, and Dependencies
State includes remote repositories, local object caches, Git config (`lfs.url`, `lfs.ssh.autoMultiplex`, `lfs.concurrentTransfers`), and trace logs. Dependencies include `setup_pure_ssh`, `ssh_remote`, `compare_version`, `assert_server_object`, `assert_remote_object`, and `git lfs fsck`.

## Integration Points, Risks, and Test Signals
Integration points are HTTP batch API, `git-lfs-authenticate`, pure SSH `git-lfs-transfer`, transfer queue ordering, and hash algorithm negotiation. Signals include upload progress, batch JSON order, unsupported hash errors, trace counts for SSH sessions, object assertions, and `fsck`. Risks are version-specific Git behavior and brittle trace regexes.
