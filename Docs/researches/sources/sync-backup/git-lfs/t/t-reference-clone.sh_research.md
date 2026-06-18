<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-reference-clone.sh -->
# sources/sync-backup/git-lfs/t/t-reference-clone.sh

Purpose: validates Git LFS behavior when cloning or fetching with Git alternate object stores created by `git clone --reference`.

Important APIs/functions: defines `assert_same_inode`; uses `setup_remote_repo_with_file`, `clone_repo`, `git clone --reference`, `git lfs pull`, `git lfs fetch`, and filesystem inode checks.

Control flow: first creates a source clone with LFS media, then clones a second repository with `--reference` and confirms the LFS object is linked/reused rather than duplicated. The fetch case verifies later LFS downloads can also use referenced local storage.

State and persistence: creates alternate object references and media files under `.git/lfs/objects`; relies on inode equality for hardlink/shared-storage checks where supported.

Dependencies and integration points: integrates with Git alternates/reference clone setup, local media storage lookup, LFS fetch/pull, and filesystem semantics.

Risks: hardlink/reference handling is platform-sensitive; regressions could duplicate large files, fail to find referenced objects, or corrupt shared local media.

Test signals: two cases cover clone-time and fetch-time reuse of reference clone storage.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-reference-clone.sh -->
