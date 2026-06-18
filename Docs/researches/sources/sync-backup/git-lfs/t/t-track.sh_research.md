<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track.sh -->
# sources/sync-backup/git-lfs/t/t-track.sh

Purpose: broad suite for `git lfs track`, including attributes listing, duplicate detection, dry-run/verbose output, directory patterns, line endings, outside-repo errors, symlinks, forbidden patterns, lockable/read-only behavior, escaping, global/system attributes, and JSON output.

Important APIs/functions: uses `git lfs track`, `assert_attributes_count`, `assert_pointer`, file mode helpers, `compare_version`, `native_path_escaped`, and `.gitattributes` direct inspection.

Control flow: starts with ordinary pattern tracking/listing and excluded pattern output. It then validates no-excluded, verbose, dry-run, directories with spaces, no trailing newline, CRLF/autocrlf cases, outside-repo and `.git` directory errors, path representation duplicates, absolute paths, symlinked directories, blocklisted files/globs, lockable toggling and read-only transitions, escaped literals and glob patterns, symlinked repositories, hook installation suppression, comments, current-directory prefixes, global/system attributes, verbose matching logs, and structured JSON output.

State and persistence: creates many repos, writes `.gitattributes` in working tree, `.git/info/attributes`, global/system attributes files, modifies core.autocrlf, file permissions, hooks, symlinks, and committed pointer content.

Dependencies and integration points: integrates with Git attributes parsing/writing, path quoting/escaping, Git config scope, clean filter, lockable file mode handling, hook installation, and JSON output code.

Risks: `track` writes persistent repository policy. Bugs can corrupt `.gitattributes`, mishandle special filenames, track forbidden files, flip file writability incorrectly, or produce incompatible JSON for scripts.

Test signals: twenty-plus cases cover normal listing, option modes, line-ending preservation, repository-boundary errors, symlinks, forbidden patterns, lockable transitions, escapes/globs/spaces, comments, scoped attributes, verbose matching, and JSON schema.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track.sh -->
