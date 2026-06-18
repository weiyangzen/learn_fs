<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_untrack.go -->
# sources/sync-backup/git-lfs/commands/command_untrack.go

Purpose: implements `git lfs untrack`, removing matching LFS filter lines from the local `.gitattributes` file.

Important APIs/types/functions: `untrackCommand` and `removePath`; shared `escapeAttrPattern`, `unescapeAttrPattern`, `tools.TrimCurrentPrefix`, and `installHooks`.

Control flow: sets up working copy, installs hooks, prints usage with no args, reads `.gitattributes`, recreates it, scans each line, preserves non-LFS lines, removes LFS filter lines whose first field matches any requested pattern after current-directory trimming and escaping, and prints untracking messages.

State and persistence behavior: truncates and rewrites `.gitattributes`. If the file does not exist it returns silently.

Dependencies/integration points: depends on track escaping rules and hook installation. It only operates on the default local attributes file, not global/system attributes.

Risks and test signals: risks include truncating before scanner completes, losing original line endings/comments around removed lines, matching only first field and `filter=lfs` substring, and no scanner error handling. Test signals include removing one/multiple tracked patterns, preserving non-LFS and unmatched lines, missing `.gitattributes`, escaped spaces/hash patterns, and no-arg usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/command_untrack.go -->
