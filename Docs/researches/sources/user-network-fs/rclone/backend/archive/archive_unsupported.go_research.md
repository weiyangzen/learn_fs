# sources/user-network-fs/rclone/backend/archive/archive_unsupported.go

Purpose: Provides a buildable `archive` package stub on unsupported Plan 9 platforms.

Important APIs/types/functions: Build tag `//go:build plan9`; only declares package `archive`.

Control flow: On Plan 9, this file is selected while `archive.go` is excluded, preventing "no buildable Go source files" errors.

State and persistence: No state.

Dependencies and integration points: Integrates with Go build constraints and packages that import `backend/archive`.

Risks: Archive backend functionality is absent on Plan 9. Callers expecting registration will not get the real backend there.

Test signals: Cross-compilation/compile-all tests for Plan 9 are the signal.
