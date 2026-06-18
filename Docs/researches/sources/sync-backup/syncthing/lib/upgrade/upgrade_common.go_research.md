# sources/sync-backup/syncthing/lib/upgrade/upgrade_common.go

Purpose: common upgrade data structures, single-flight locking, version comparison, and release asset naming.

Important APIs and control flow: `Release`, `Asset`, and `ReleaseCompatibility` model release metadata. Errors describe no download, no selectable version, unsupported upgrade, and in-progress upgrade. `To` and `ToURL` acquire `upgradeUnlocked`, find current executable, call platform-specific upgrade functions, and only unlock on failure so a successful upgrade cannot be repeated in-process. `CompareVersions` parses release and prerelease parts, handles optional `v`/`V`, ignores build metadata, treats 0.x and 1.x major transition specially, compares prerelease numbers/strings semver-style, and returns a `Relation`. `releaseNames` restricts acceptable asset prefixes by OS/arch and tag, with macOS name aliases.

State and persistence: `upgradeUnlocked` is a process-wide channel semaphore. Upgrade functions rename binaries elsewhere.

Dependencies and integration: used by app/API upgrade flows and usage-report upgrade flags.

Risks: `versionParts` treats invalid numeric release fields as zero. Single-flight unlock semantics assume process restart after successful upgrade. Tests heavily cover comparison and selection.
