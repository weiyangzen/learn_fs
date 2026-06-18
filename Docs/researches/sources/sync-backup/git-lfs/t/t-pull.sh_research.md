# sources/sync-backup/git-lfs/t/t-pull.sh

Purpose: comprehensive integration suite for `git lfs pull`, including object download, checkout hydration, include/exclude filters, filesystem conflict handling, remotes, missing objects, permissions, bare repositories, partial clone/sparse checkout, and pointer extensions.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `assert_pointer`, `assert_server_object`, `assert_local_object`, `assert_clean_status`, `assert_clean_index`, `assert_clean_worktree_with_exceptions`, `git lfs pull`, `git lfs fetch`, `git lfs checkout`, `git clone`, config keys for fetch include/exclude and remote URLs, hard-link checks, sparse checkout, partial clone flags, and extension helpers.

Control flow: the first large test pushes several `.dat` files, clears local object state, and repeatedly pulls with default remote, explicit remote, config filters, command-line filters, changed filter sets, and filename encodings. Conflict suites verify pull skips paths blocked by directory/file/symlink and case-collision conflicts while still downloading objects and keeping the index clean. Later tests cover changed files, hard-link breakage, operation without clean filter, raw remote URLs, multiple remotes, invalid `insteadOf`, merge conflicts, missing objects, outside-repo errors, read-only directories/files, empty-file mtime stability, bare repo fetch-only behavior, partial clone with sparse checkout and index state, and extension-aware pointer downloads.

State/persistence behavior: the command populates `.git/lfs/objects`, writes hydrated worktree files, respects modified/read-only files, preserves index cleanliness, and in bare repos avoids a worktree checkout. Tests deliberately remove object caches, create conflicts, alter remotes/config, and compare file contents/permissions/mtimes.

Dependencies/integration points: integrates transfer queue downloads, checkout scanner, path filters, Git remote resolution, filesystem conflict detection, symlink and case-sensitivity behavior, hard-link safety, partial clone filters, sparse index/checkout, and LFS extension processing.

Risks/test signals: regressions can overwrite user changes, fail to hydrate objects, dirty the index, mishandle conflicting paths, preserve unsafe hard links, use wrong remotes, or fail in sparse/partial environments. Several tests are platform-sensitive for symlinks, case handling, and read-only permissions.
