# sources/sync-backup/kopia/snapshot/restore/shallow_helper.go

Purpose: helper functions for recognizing and safely deleting shallow placeholder sidecar files.

Important APIs/types/functions: `PathIfPlaceholder` and `SafeRemoveAll`.

Control flow: `PathIfPlaceholder` returns the base path when a path ends with `localfs.ShallowEntrySuffix`, otherwise `""`. `SafeRemoveAll` checks `SafelySuffixablePath`; if true it removes `path + suffix` through `ospath.SafeLongFilename`, otherwise it returns nil because such a placeholder could not have been created safely.

State and persistence: only `SafeRemoveAll` mutates filesystem state, and only by removing placeholder sidecars, not the real restored path.

Dependencies and integration points: called by local restore after writing real directories/files and by shallow restore cleanup paths.

Risks and test signals: correctness depends on the platform-specific suffixability check. The test sweeps near filename limits to ensure cleanup succeeds whether or not the sidecar could be created.
