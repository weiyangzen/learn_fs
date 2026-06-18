<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/context.go -->
# sources/sync-backup/git-lfs/errors/context.go

## Research

`context.go` defines helpers for contextual metadata on wrapped errors. The unexported `withContext` interface requires `Set`, `Get`, `Del`, and `Context`. Exported helpers `SetContext`, `GetContext`, `DelContext`, and `Context` no-op or return empty values for ordinary errors.

State lives inside `wrappedError.context` maps in `types.go`. Integration is used by smudge and clean pointer errors to attach OID, filename, pointer, or byte data, and by callers that need diagnostic details without type assertions. Risks include no synchronization around context maps, value receiver methods sharing the same map, `GetContext` returning empty string while `Context` returns nil for non-wrapped errors, and context not propagating through Go 1.20 joined errors. `errors_test.go` covers context on plain and wrapped errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/context.go -->
