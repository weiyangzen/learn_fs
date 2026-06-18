# sources/sync-backup/kopia/repo/logging/ctx.go

Purpose: stores module logger factories in context and caches per-module loggers.

Important APIs/types/functions: `loggerCache`, `WithLogger`, `WithAdditionalLogger`, `loggerFactoryFromContext`, and `loggerCache.getLogger`.

Control flow: `WithLogger` installs a `loggerCache`, substituting the null factory for nil. `getLogger` uses `sync.Map` and `LoadOrStore` to create one logger per module. `WithAdditionalLogger` wraps the existing context factory with `Broadcast`.

State/persistence behavior: context-local in-memory cache only; no durable state.

Dependencies/integration: consumed by `logging.Module` across repository packages and by tests that inject writer/test loggers.

Risks/test signals: context values use a package-private key, reducing collision risk. Type assertions assume only this package writes that key. Tests cover additional logger fan-out and null/default behavior.
