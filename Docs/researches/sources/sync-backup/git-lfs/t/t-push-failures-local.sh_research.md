<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-local.sh -->
# sources/sync-backup/git-lfs/t/t-push-failures-local.sh

Purpose: exercises local-object failure behavior for `git lfs push`, especially `lfs.allowincompletepush` and the SSH `git-lfs-transfer` path. It validates that missing or corrupt local LFS media can be either tolerated with an incomplete-push warning or rejected before remote upload.

Important APIs/functions: sources `testlib.sh`; uses `setup_remote_repo`, `clone_repo`, `setup_pure_ssh`, `ssh_remote`, `git lfs track`, `git lfs push`, `git push`, `delete_local_object`, `corrupt_local_object`, `assert_server_object`, and `refute_server_object`.

Control flow: each `begin_test` creates an isolated remote and clone, tracks `*.dat`, commits LFS files, mutates local media storage, and pushes. The first pair enables `lfs.allowincompletepush` and expects Git data to push while selected LFS objects are absent remotely. The default and explicit false cases expect failure messages. The final cases replace object content with zero-byte corrupt files and verify checksum/size validation failure.

State and persistence: mutates `.git/lfs/objects`, repository config, branch history, and remote test-server storage under `REMOTEDIR`. SSH variants set `lfs.url` to a pure SSH URL and exercise packet-transfer persistence on the same test repository state.

Dependencies and integration points: depends on the LFS pre-push hook, transfer queue, object scanner, local media verifier, test HTTP server, and optional `git-lfs-transfer` binary. Integrates with `testhelpers.sh` object helpers for both local disk and remote server assertions.

Risks: local failure handling is sensitive to config precedence, hook-vs-manual push differences, transfer adapter parity, and stale remote state. Corrupt-object checks guard against uploading invalid content or reporting success after a partial local read.

Test signals: eight tests cover allow-missing true, false, default rejection, corrupt object rejection, and equivalent pure SSH transfer cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-push-failures-local.sh -->
