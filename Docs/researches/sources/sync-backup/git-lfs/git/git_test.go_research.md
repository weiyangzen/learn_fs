# sources/sync-backup/git-lfs/git/git_test.go

Purpose: integration-heavy tests for the `git` package ref, branch, worktree, version, tracked-file, changed-file, remote URL, and object-ID helpers. The file uses temporary repositories from `t/cmd/util` to exercise real Git subprocess behavior rather than isolated parser logic.

Important APIs/types/functions: `Ref.Refspec`, `ParseRef`, `CurrentRef`, `Configuration.CurrentRemoteRef`, `RemoteRefNameForCurrentBranch`, `ResolveRef`, `RecentBranches`, `GetAllWorktrees`, `IsVersionAtLeast`, `GitAndRootDirs`, `GetTrackedFiles`, `LocalRefs`, `GetFilesChanged`, `ValidateRemoteURL`, `RefType.Prefix`, `RemoteURLs`, `MapRemoteURL`, `HasValidObjectIDLength`, and `IsZeroObjectID`.

Control flow: tests create commits, branches, tags, remotes, worktrees, staged files, and deleted files; then assert helper output against expected refs, paths, or booleans. Some tests gate on Git version, especially worktree behavior. Remote URL tests write local config and then query normal and push URLs.

State/persistence behavior: most cases mutate actual `.git` state: refs, packed/unpacked worktrees, config, index state, and working-tree deletion/staging. The tests verify functions see both committed and index state and do not rely only on the working tree.

Dependencies/integration: depends on the local Git binary, filesystem temp repos, `tools.CanonicalizePath`, and helper sorters for refs/worktrees/pointers. It covers behavior that other files in this group rely on, such as ref classification used by history rewriting and scanner range construction.

Risks/test signals: tests are sensitive to Git version, platform path normalization, branch default names, and real Git command behavior. Strong signals include correct ref names/SHAs, worktree pruning flags, stable file-change lists, and URL mapping. The file does not test every implementation path directly, but it establishes broad behavioral contracts for callers.
