<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-usage.sh -->
# sources/sync-backup/git-lfs/t/t-usage.sh

Purpose: checks top-level usage output when no Git LFS subcommand is supplied.

Important APIs/functions: runs `git lfs` without command and greps usage/help output.

Control flow: invokes the binary with no arguments and verifies the command reports usage instead of crashing or silently succeeding.

State and persistence: no repository or remote state required beyond test harness environment.

Dependencies and integration points: integrates with CLI command dispatch and help text generation.

Risks: broken usage output affects discoverability and scripts that rely on non-command invocation behavior.

Test signals: one no-command usage test.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-usage.sh -->
