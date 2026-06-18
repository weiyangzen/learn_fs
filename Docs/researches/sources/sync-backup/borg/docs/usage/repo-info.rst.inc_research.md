# sources/sync-backup/borg/docs/usage/repo-info.rst.inc

Purpose: Documents `borg repo-info`, a read-only command that displays detailed repository information.

Important APIs/types/functions: CLI contract is `borg [common options] repo-info [options]` with `--json` for machine-readable output.

Control flow: Runtime opens the repository, reads repository/manifest/cache statistics as needed, and emits text or JSON. Documentation generation follows the common command include pattern.

State and persistence: Should not mutate repository state except incidental cache reads/refreshes depending on implementation. JSON output creates an automation contract.

Dependencies and integration points: Integrates with repository backends, statistics collection, common repository selection, and monitoring scripts.

Risks: JSON schema drift can break automation. Large repositories may make info gathering expensive if it requires cache/stat scans.

Test signals: Validate text and JSON output against known repositories, empty repositories, encrypted/authenticated modes, and stale/missing cache states.
