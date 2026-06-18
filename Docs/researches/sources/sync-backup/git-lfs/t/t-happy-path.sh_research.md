# sources/sync-backup/git-lfs/t/t-happy-path.sh

## Purpose

Baseline end-to-end Git LFS smoke tests. It verifies tracking, pointer creation, upload, clone/pull download, non-origin remote use, branch-ref-aware object storage, tracked upstream refs, `git lfs clone --exclude`, and cleanup of stale temporary local objects.

## Important APIs, control flow, and dependencies

The tests use `setup_remote_repo`, `setup_remote_repo_with_file`, `clone_repo`, `git lfs track`, `git add/commit/push/pull`, `assert_pointer`, `assert_server_object`, `assert_local_object`, `git lfs clone`, branch config (`push.default`, `branch.main.merge`), and `git lfs env` for temp cleanup. The temp-object test creates files under `.git/lfs/tmp/objects` whose names correspond or do not correspond to complete local objects.

## State, dependencies, integration points, risks, and test signals

State includes working tree content, pointer blobs, local and remote LFS object stores, remote names, branch refs, and temporary object files. Integration points are clean/smudge filters, pre-push upload, pull smudge/download, ref-qualified server object storage, upstream tracking, and local storage janitor behavior. Risks include missing first-push upload, assuming only `origin`, wrong ref metadata for required-branch servers, and deleting unrelated tmp objects. Signals are commit/push greps, content equality, pointer assertions, local/server object assertions, and tmp file existence/refutation checks.
