# sources/sync-backup/kopia/snapshot/restore/long_paths_windows.go

Purpose: Windows filename-length check for shallow placeholder suffixing.

Important APIs/types/functions: `MaxFilenameLength = 255` and `SafelySuffixablePath`.

Control flow: the check uses `filepath.Base(path)` plus `localfs.ShallowEntrySuffix`, matching the per-component compatibility limit used by Linux and macOS rather than full Windows long-path capacity.

State and persistence: no state is changed; callers use the boolean to avoid impossible placeholder sidecar operations.

Dependencies and integration points: paired with Windows long path normalization in local restore and with `SafeRemoveAll` shallow cleanup.

Risks and test signals: the conservative 255 value may reject some paths Windows could represent with long-path APIs, but it prevents sidecar cleanup errors. Boundary behavior is covered by `shallow_helper_test.go`.
