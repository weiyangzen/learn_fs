<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-version.sh -->
# sources/sync-backup/git-lfs/t/t-version.sh

Purpose: checks that `git lfs --version` is accepted as a synonym for `git lfs version`.

Important APIs/functions: invokes both version forms and compares output.

Control flow: runs version commands and asserts synonym behavior.

State and persistence: no mutable repo state.

Dependencies and integration points: integrates with CLI flag parsing and version output code.

Risks: command-line compatibility regressions can break package managers and diagnostic scripts.

Test signals: one version synonym test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-version.sh -->
