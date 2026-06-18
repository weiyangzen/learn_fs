# sources/sync-backup/git-lfs/t/t-post-checkout.sh

Purpose: verifies the Git LFS post-checkout hook updates lockable-file permissions correctly after clone, branch checkout, path checkout, and lock state changes.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track --lockable`, `lfstest-testutils addcommits`, `git checkout`, `git lfs lock`, `assert_file_writeable`, and `refute_file_writeable`.

Control flow: the main test builds a history with lockable `.dat` files and non-lockable `.big` files across `main` and `branch2`, pushes both branches, reclones, then checks contents and write permissions on initial checkout, branch checkout, path checkout after deleting files, and checkout after locking selected paths. The subdirectory test repeats the same lockable behavior with `bin/*.dat` patterns.

State/persistence behavior: repository state includes `.gitattributes`, LFS objects, branch histories, lock records, and filesystem read-only bits. The hook must update permissions without corrupting file contents, including files that were read-only before checkout.

Dependencies/integration points: integrates Git checkout hooks, LFS smudge/checkout behavior, lockable attribute matching, remote locks, pathspec checkout, and platform filesystem permission support.

Risks/test signals: failures indicate lockable files remain writable when they should be protected, locked files become read-only incorrectly, or checkout fails to hydrate/update content. Permission assertions can be platform-sensitive.
