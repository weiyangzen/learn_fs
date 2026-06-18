# sources/sync-backup/syncthing/lib/upgrade/upgrade_unsupp.go

Purpose: unsupported build implementation for the upgrade package.

Important APIs and control flow: built for `noupgrade` or iOS. Sets `DisabledByCompilation = true`. `upgradeTo`, `upgradeToURL`, and `LatestRelease` all return `ErrUpgradeUnsupported`.

State and persistence: no state and no binary modifications.

Dependencies and integration: allows callers to compile against the same API while disabling upgrades. Usage reporting reads `DisabledByCompilation` to report upgrade capability.

Risks and signals: simple build-tag fallback. Tests with `!noupgrade` do not exercise this file.
