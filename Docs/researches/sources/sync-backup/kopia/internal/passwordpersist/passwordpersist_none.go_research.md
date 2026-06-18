# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_none.go

Purpose: explicit strategy that disables password persistence.

Important APIs/types/functions: `None`, `noneStrategy`, and methods implementing `Strategy`.

Control flow: `GetPassword` returns `ErrPasswordNotFound`; `PersistPassword` returns `ErrUnsupported`; `DeletePassword` succeeds as a no-op.

State and persistence behavior: stores nothing.

Dependencies and integration points: useful for users or environments that do not want secrets persisted.

Risks and test signals: callers must handle unsupported persistence as nonfatal when configured with fallbacks.
