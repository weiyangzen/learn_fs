# sources/sync-backup/git-lfs/t/t-post-merge.sh

Purpose: verifies the post-merge hook reapplies read-only permissions to lockable files changed by a merge.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track --lockable`, `lfstest-testutils addcommits`, `git merge`, `git reset --hard`, `GIT_LFS_SET_LOCKABLE_READONLY`, `assert_file_writeable`, and `refute_file_writeable`.

Control flow: the test creates a main/branch2 history with lockable `.dat` files and non-lockable `.big` files, reclones, verifies initial content and permissions, then performs a merge with readonly handling disabled to demonstrate files would stay writable. It resets and repeats the merge with normal settings, expecting branch-updated lockable files to become read-only while contents are correct.

State/persistence behavior: persisted state includes branch histories, LFS objects, and `.gitattributes`; worktree state includes merge results and filesystem permissions. The hook's side effect is permission correction after Git updates files.

Dependencies/integration points: integrates Git merge hooks, lockable attribute resolution, LFS checkout/smudge behavior, environment-controlled readonly behavior, and branch-tracking from the fixture remote.

Risks/test signals: failures indicate merged lockable files are left writable, merge content is not hydrated correctly, or the readonly environment escape changes behavior unexpectedly.
