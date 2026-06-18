## sources/sync-backup/kopia/internal/cache/export_test.go

Purpose: exposes an internal persistent cache method for tests.

Important APIs/types/functions: `PersistentCache.TestingGetFull`.

Control flow, state, and persistence: delegates to unexported `getFull`, writing cached content into a `gather.WriteBuffer` and returning whether the key was found.

Dependencies and integration points: enables external test packages to inspect full-cache content without broadening production API.

Risks and test signals: compiled only in tests. Keep narrow to avoid hiding production API needs.
