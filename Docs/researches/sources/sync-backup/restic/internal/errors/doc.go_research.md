## sources/sync-backup/restic/internal/errors/doc.go

Purpose: package documentation for restic's internal error compatibility layer. It declares package `errors` and has no exported APIs beyond documentation. Control flow, state, and persistence are absent. Integration point is Go documentation and the package boundary for wrappers around standard and pkg/errors behavior. Risks are minimal; code behavior lives in `errors.go` and `fatal.go`. No direct tests.
