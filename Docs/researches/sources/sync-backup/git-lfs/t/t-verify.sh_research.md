<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-verify.sh -->
# sources/sync-backup/git-lfs/t/t-verify.sh

Purpose: verifies transfer verification retry behavior, including successful retry, no-retry success, insufficient retries, and malformed retry config.

Important APIs/functions: uses content names that trigger verify responses, Git config retry settings, `git push`, log greps, and server object checks.

Control flow: creates LFS objects that require verify action retries, pushes with configured retry counts, and checks whether upload succeeds or fails. A malformed config case verifies fallback/error handling.

State and persistence: mutates Git config and remote LFS storage; uses server-triggered verify behavior.

Dependencies and integration points: integrates with batch verify action handling, retry scheduler, transfer queue, config parsing, and error reporting.

Risks: verification protects integrity after upload. Retry bugs can falsely fail transient verifies or accept objects without required verification.

Test signals: four cases cover retries, success without retry, insufficient retries, and bad `.gitconfig`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-verify.sh -->
