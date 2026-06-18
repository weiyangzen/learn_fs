<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testenv.sh -->
# sources/sync-backup/git-lfs/t/testenv.sh

Purpose: shared environment bootstrap for Git LFS integration tests. It detects platform traits, sets paths and environment variables, creates temp/trash directories, locates the test server files, and sources `testhelpers.sh`.

Important APIs/functions: defines `native_path` and `resolve_symlink`; exports `ROOTDIR`, `BINPATH`, `TRASHDIR`, `REMOTEDIR`, credential/certificate paths, `GIT_LFS_FORCE_PROGRESS`, `GIT_CONFIG_NOSYSTEM`, `GIT_SSH`, `GIT_TEMPLATE_DIR`, and `LC_ALL`.

Control flow: detects Windows/Mac/Linux, selects checksum tool and path separator, resolves or creates `GIT_LFS_TEST_DIR`, derives per-test `TRASHDIR`, defines remote server metadata paths, sets Git/LFS environment defaults, clears Git env vars that would leak from callers, creates directories, disables Windows GUI askpass, and loads helpers.

State and persistence: creates a temp root and per-test trash directory, exports temp-root cleanup markers, and sets process-wide environment variables used by every test file.

Dependencies and integration points: integrates with compiled binaries under `bin`, fake SSH command `lfs-ssh-echo`, template fixtures, lfstest server URL/cert files, and all shell test scripts via `testlib.sh`.

Risks: incorrect environment isolation can leak user Git config, break path handling on Windows/Mac, reuse stale server state, or run tests inside the source repository.

Test signals: indirectly covered by all sourced shell tests; helper functions are exercised on platform-specific paths and symlink resolution.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testenv.sh -->
