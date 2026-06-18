# sources/sync-backup/bup/test/int/test_resolve.py

Purpose: comprehensive integration coverage for repository path resolution through local and file-remote repository implementations, including root normalization, branch/revlist contents, tags, latest links, symlink following, bad symlinks, ENOTDIR paths, relative parent resolution, directory symlinks, and symlink loops.

Important APIs/types/functions: `prep_and_test_repo()`, `_test_resolve()`, `_test_resolve_loop()`, `LocalRepo`, `repo_for_url`, `URL`, `repo.resolve`, `vfs.clear_cache`, `vfs.contents`, `vfs.IOError`, `vfs.RevList`, `vfs.Commit`, `vfs.FakeLink`, `vfs.Item`, `tree_dict`, `exc`, `exo`, and bup CLI commands `init`, `index`, `save`, `tag`.

Control flow: setup creates a source tree with a file, directory, file symlink, directory symlink, and bad symlink, saves it with a fixed timestamp, and tags the branch. The test reads Git object IDs, builds expected VFS items from independent tree parsing, clears the VFS cache before each case, then resolves many normalized paths. It validates root, `.tag`, branch, latest save, file, bad symlink with and without following, file symlink with and without following, missing leaves, file-as-directory ENOTDIR cases, relative lookup with a file parent, and directory symlink trailing-slash behavior. Separate tests run the same body for `LocalRepo` and `repo_for_url(file://...)`; loop tests expect ELOOP for a self-referential symlink.

State and persistence behavior: creates real repositories under `tmpdir`, mutates `GIT_DIR`/`BUP_DIR` and `git.repodir`, writes Git refs, tags, trees, symlinks, and cached VFS entries. Cache clearing is part of the tested state because metadata may be promoted after traversal.

Dependencies/integration points: ties together CLI save/index, Git ref inspection, VFS tree/materialized metadata semantics, local and remote repository adapters, URL-based repository selection, and independent `buptest.vfs.tree_dict` validation.

Risks and test signals: expected tuples are sensitive to cache metadata promotion and exact save timestamp formatting. Tests assume symlink support. Signals include exact resolution terminus lists, errno values for ENOTDIR/ELOOP, and matching contents for root, branch, tag, and latest directories.
