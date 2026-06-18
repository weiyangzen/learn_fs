# sources/sync-backup/kopia/snapshot/restore/long_paths_unix.go

Purpose: Unix implementation of filename-length checks for shallow placeholder suffixing.

Important APIs/types/functions: `MaxFilenameLength = syscall.NAME_MAX` and `SafelySuffixablePath`.

Control flow: `SafelySuffixablePath` checks `len(filepath.Base(path)) + len(localfs.ShallowEntrySuffix)` against the platform name limit. Directory components are irrelevant because only the final placeholder filename is extended.

State and persistence: no persistent state; it protects later `os.RemoveAll` and placeholder creation from avoidable `ENAMETOOLONG` failures.

Dependencies and integration points: used by `restore.SafeRemoveAll` and shallow directory placeholder decisions on non-Windows, non-Plan9 builds.

Risks and test signals: byte length rather than rune or filesystem encoding details is used. The companion test sweeps lengths around `MaxFilenameLength` and expects cleanup to be harmless even when the placeholder cannot exist.
