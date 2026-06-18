<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-tempfile.sh -->
# sources/sync-backup/git-lfs/t/t-tempfile.sh

Purpose: validates cleanup of old Git LFS temporary files and directories without deleting recent temp artifacts.

Important APIs/functions: uses temp-file creation under the LFS temp area, timestamp manipulation, `git lfs prune` or temp cleanup command paths, and filesystem assertions.

Control flow: creates temp files/directories with ages around the one-hour cutoff, runs cleanup, and verifies only old temp artifacts are removed.

State and persistence: manipulates files under repository LFS temp storage and their mtimes.

Dependencies and integration points: integrates with temp naming conventions, filesystem mtime behavior, and cleanup/prune logic.

Risks: overly aggressive cleanup can delete active transfers; too-conservative cleanup leaks disk space.

Test signals: one cutoff-focused cleanup test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-tempfile.sh -->
