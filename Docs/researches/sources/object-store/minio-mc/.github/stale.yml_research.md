<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/.github/stale.yml -->
# sources/object-store/minio-mc/.github/stale.yml

## Purpose
Configuration for stale issue/PR automation in the MinIO client repository.

## Important APIs, types, and functions
Sets `daysUntilStale: 90`, `daysUntilClose: 30`, exempts `security` and `pending discussion`, uses label `stale`, posts a stale comment, and limits actions with `limitPerRun: 1`.

## Control flow
The probot stale app marks inactive items stale, then later closes stale items unless exempted or updated.

## State and persistence behavior
No application persistence. It changes GitHub labels/comments/closed state.

## Dependencies and integration points
Integrates GitHub issue lifecycle, repository labels, and security triage policy.

## Risks and test signals
The comment says closure after 21 days while `daysUntilClose` is 30, so user-facing text and automation differ. Signals are bot label/close activity and config validation by the stale app.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/.github/stale.yml -->
