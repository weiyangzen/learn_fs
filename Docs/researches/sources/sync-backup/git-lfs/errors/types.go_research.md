<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types.go -->
# sources/sync-backup/git-lfs/errors/types.go

## Research

`types.go` defines the concrete wrapped error hierarchy and inspection helpers. It includes behavior predicates for fatal, not implemented, auth, smudge, clean pointer, not-a-pointer, pointer scan, bad pointer key, protocol, download declined, unprocessable entity, retriable, and retriable-later errors. `wrappedError` embeds a `pkg/errors` cause/formatter plus a context map.

Constructors wrap underlying errors and attach marker methods. `NewRetriableLaterError` parses Retry-After as seconds or RFC1123 time; `IsRetriableError` also recognizes temporary/timeout `url.Error` causes; `ExitStatus` extracts process exit status. `parentOf` recursively inspects `Cause` to let outer wrappers inherit inner marker behavior. State is per-error context and optional retry timestamp. Dependencies include `net/url`, `exec`, `syscall`, `time`, translation, and `pkg/errors`. Risks include brittle type assertion in `StandardizeBadPointerError`, joined error incompatibility, `parentOf` skipping only through cause chains, mutable unsynchronized contexts, and platform-specific wait status. Tests cover marker nesting and URL temporary/timeout retry classification.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types.go -->
