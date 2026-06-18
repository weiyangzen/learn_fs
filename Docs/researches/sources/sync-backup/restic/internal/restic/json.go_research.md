
# sources/sync-backup/restic/internal/restic/json.go

Purpose: provides generic helpers for loading and saving JSON-encoded unpacked repository files.

`LoadJSONUnpacked` loads bytes through a `LoaderUnpacked`, decodes JSON with `json.Unmarshal`, and wraps errors with file type and ID. `SaveJSONUnpacked` marshals an item with `json.Marshal` and saves it through `SaverUnpacked`, preserving the generic file-type parameter. Both functions are intentionally thin wrappers that centralize error context.

State and persistence are delegated to repository implementations: callers use these helpers for config, locks, and other unpacked JSON files. Integration points include `LoadConfig`, `SaveConfig`, lock creation/loading, and any future JSON metadata files. Risks include full-buffer JSON processing, loss of streaming behavior, and type mismatches only detected at runtime by JSON. Test coverage is indirect through config and lock tests.
