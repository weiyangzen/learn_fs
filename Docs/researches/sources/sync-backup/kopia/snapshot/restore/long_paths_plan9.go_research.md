# sources/sync-backup/kopia/snapshot/restore/long_paths_plan9.go

Purpose: Plan 9 implementation of placeholder suffix safety checks for shallow restore cleanup.

Important APIs/types/functions: `MaxFilenameLength` and `SafelySuffixablePath`.

Control flow: the check returns true when the whole path length plus `localfs.ShallowEntrySuffix` fits within `math.MaxUint16`. Unlike Unix/Windows variants, it does not inspect only the base name.

State and persistence: no state is changed; the result gates whether `SafeRemoveAll` may attempt to remove a placeholder sidecar.

Dependencies and integration points: used by shallow restore output and cleanup helpers to avoid generating impossible long placeholder filenames.

Risks and test signals: the constant is derived by code inspection and may be looser than a specific Plan 9 filesystem limit. The shared shallow helper test exercises boundary behavior through the platform-specific limit.
