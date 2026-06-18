## sources/sync-backup/restic/internal/filter/doc.go

Purpose: package documentation for path filtering used by backup exclude/include rules. It describes shell-style patterns and recursive `**` matching. No runtime APIs live here. Control flow, state, persistence, and dependencies are absent beyond package declaration. Integration point is Go documentation for `filter.Match`, `List`, and exclude helpers. Risks are documentation drift if pattern semantics change without updating this file. Tests for actual semantics live in filter test files.
