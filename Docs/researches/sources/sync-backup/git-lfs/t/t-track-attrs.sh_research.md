<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-attrs.sh -->
# sources/sync-backup/git-lfs/t/t-track-attrs.sh

Purpose: tests `git lfs track` modes that should not modify `.gitattributes`: `--no-modify-attrs` and `--dry-run`.

Important APIs/functions: uses `git lfs track`, `.gitattributes` inspection, `git status`, and output greps.

Control flow: runs track with no-modify or dry-run flags against patterns, checks user-facing output, and asserts attributes files remain unchanged.

State and persistence: initializes temporary Git repositories and intentionally avoids persisting new attributes for these modes.

Dependencies and integration points: integrates with track command option parsing, attributes writer, and status/index behavior.

Risks: dry-run/no-modify regressions can unexpectedly alter repositories or produce misleading output for automation.

Test signals: two tests cover no-modify attributes and dry-run behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-track-attrs.sh -->
