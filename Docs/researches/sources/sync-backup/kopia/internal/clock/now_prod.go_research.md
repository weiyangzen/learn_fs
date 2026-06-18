# sources/sync-backup/kopia/internal/clock/now_prod.go

Purpose: production implementation of `clock.Now` for non-`testing` builds.

Important APIs/types/functions: build tag `!testing` and function `Now() time.Time`.

Control flow: calls `time.Now()` and immediately passes the result through `discardMonotonicTime`.

State and persistence behavior: no state. It returns wall-clock timestamps without monotonic components, which are safe to compare after serialization and across long sleeps.

Dependencies/integration: used by packages such as cache, content logging, and epoch manager when no injected time function is supplied.

Risks/test signals: no direct tests in this file. Runtime correctness depends on the shared `discardMonotonicTime` helper and callers accepting wall-clock rather than monotonic timing.
