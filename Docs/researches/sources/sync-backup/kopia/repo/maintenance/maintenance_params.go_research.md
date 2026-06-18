# sources/sync-backup/kopia/repo/maintenance/maintenance_params.go

Purpose: stores repository-wide maintenance configuration in manifests.

Important APIs/types/functions: `Params`, `CycleParams`, `DefaultParams`, `HasParams`, `IsOwnedByThisUser`, `GetParams`, `SetParams`, and `manifestIDs`.

Control flow: maintenance params are looked up by fixed manifest labels. Missing params return defaults; multiple params choose the latest manifest ID. Setting params replaces manifests with the maintenance labels.

State/persistence behavior: persists owner, quick/full cycle intervals, log retention, object-lock extension, and list parallelism as JSON manifest data. Owner is compared to `ClientOptions.UsernameAtHost`.

Dependencies/integration: integrates the manifest manager with maintenance scheduling and ownership checks.

Risks/test signals: multiple concurrent clients can briefly create multiple manifests, so latest-pick behavior is intentional. Wrong owner prevents auto maintenance. Tested indirectly through quick maintenance ownership setup.
