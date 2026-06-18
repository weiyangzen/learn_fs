# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_multiple.go

Purpose: composes multiple password persistence strategies with fallback semantics.

Important APIs/types/functions: `Multiple`, `GetPassword`, `PersistPassword`, and `DeletePassword`.

Control flow: get returns the first successful password, skips `ErrPasswordNotFound`, and fails on other errors. Persist tries strategies until one succeeds, skips `ErrUnsupported`, and returns `ErrUnsupported` if none work. Delete calls all strategies and suppresses expected not-found/unsupported outcomes.

State and persistence behavior: state is delegated to child strategies.

Dependencies and integration points: lets Kopia prefer keyring while falling back to file or none.

Risks and test signals: delete can partially fail after earlier strategies succeeded. Tests should cover strategy ordering, fatal errors, unsupported fallback, and aggregate delete behavior.
