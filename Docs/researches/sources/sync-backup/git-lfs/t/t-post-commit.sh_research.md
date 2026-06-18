# sources/sync-backup/git-lfs/t/t-post-commit.sh

Purpose: validates the post-commit hook's lockable-file permission updates and ensures it does not traverse submodule contents.

Important APIs/functions: uses `git lfs track --lockable`, `git lfs lock`, `assert_file_writeable`, `refute_file_writeable`, `git submodule add`, and `GIT_TRACE` output inspection.

Control flow: the primary test commits lockable `.dat` files and non-lockable `.big` files, expects newly committed unlocked lockable files to become read-only, then locks two files, edits and commits them, and expects them to remain writable. A second test covers a non-LFS file marked `lockable` in `.gitattributes`, intentionally split across two commits to avoid initial-commit post-checkout behavior. The submodule test commits a submodule and uses trace output to ensure the post-commit filter logic does not enter `submodule/foo`.

State/persistence behavior: the suite mutates `.gitattributes`, committed files, lock state, file mode/read-only bits, and submodule metadata. It checks post-commit side effects on the worktree rather than remote object transfer.

Dependencies/integration points: integrates Git hooks, lockable attributes outside and inside LFS tracking, LFS locks API, submodule boundaries, and trace instrumentation.

Risks/test signals: regressions can leave lockable files editable without locks, make locked files read-only, mishandle lockable non-LFS paths, or scan into submodules. The submodule case relies on trace text matching `filepathfilter`.
