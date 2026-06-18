<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_status.go -->
# sources/sync-backup/git-lfs/commands/command_status.go

Purpose: implements `git lfs status`, reporting staged/unstaged LFS-related changes, objects to push, and porcelain/JSON scriptable status.

Important APIs/types/functions: globals `porcelain`, `statusJson`; `statusCommand`, `formatBlobInfo`, `blobInfoFrom`, `blobInfoTo`, `blobInfo`, `scanIndex`, `drainScanner`, `keyFromEntry`, `statusScanRefRange`, `JSONStatusEntry`, `JSONStatus`, `jsonStagedPointers`, `porcelainStagedPointers`, `porcelainStatusLine`, and `relativize`.

Control flow: sets up working copy, resolves current ref or empty tree, creates pointer scanner, dispatches porcelain/JSON modes early, prints branch and objects to push by scanning ref range to current remote, scans cached and uncached diff-index entries, de-duplicates entries, computes relative paths from cwd, and formats each staged/unstaged entry with source/destination blob info from LFS pointer scanner or working-tree SHA-256.

State and persistence behavior: read-only; scans Git objects/index and working-tree files. JSON output accumulates map entries in memory.

Dependencies/integration points: integrates diff-index scanner, pointer scanner, current remote ref config, Git object IDs, filesystem symlink resolution, and SHA-256 content hashing for working files.

Risks and test signals: risks include JSON mode only including entries whose source is LFS, missing scanner close in early porcelain/JSON returns, working-tree hash using SHA-256 rather than Git blob SHA, and relative path edge cases. Test signals include no commits/empty tree, staged/unstaged add/modify/delete/rename/copy, missing objects, porcelain output, JSON output, subdirectory execution, and objects-to-push scan.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_status.go -->
