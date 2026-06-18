<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/lock.yml -->
# sources/object-store/minio-mc/.github/lock.yml

## Purpose
Configuration for an issue-locking automation that locks inactive closed issues after a long quiet period.

## Important APIs, types, and functions
Important keys include `daysUntilLock: 365`, `skipCreatedBefore: false`, `exemptLabels: []`, `lockComment`, `setLockReason: true`, and `only: issues`.

## Control flow
The external lock app scans closed issues, skips exempt labels, posts the configured comment, sets the lock reason, and locks only issues after the inactivity threshold.

## State and persistence behavior
No code state. It mutates GitHub issue lock state and comments when the bot runs.

## Dependencies and integration points
Depends on the configured lock-threads GitHub app and repository labels.

## Risks and test signals
A broad empty exemption list means all closed issues are eligible. Bot dry-runs or observed locked old issues are the practical signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/lock.yml -->
