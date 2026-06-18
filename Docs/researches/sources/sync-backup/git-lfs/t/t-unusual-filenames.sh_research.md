<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unusual-filenames.sh -->
# sources/sync-backup/git-lfs/t/t-unusual-filenames.sh

Purpose: verifies pushing LFS files with unusual filenames and quoting-sensitive paths.

Important APIs/functions: uses `git lfs track`, file creation with special names, commit/push, and server object assertions.

Control flow: creates specially named files, tracks and commits them, pushes to the test server, and confirms objects arrive.

State and persistence: stores unusual paths in Git history, `.gitattributes`, local LFS objects, and remote LFS storage.

Dependencies and integration points: integrates with path quoting, Git attributes matching, clean filter, pre-push scanner, and transfer upload.

Risks: shell/Git/path escaping bugs can skip files, create invalid attributes, or fail on platforms with filename limitations.

Test signals: one push case focused on unusual names.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-unusual-filenames.sh -->
