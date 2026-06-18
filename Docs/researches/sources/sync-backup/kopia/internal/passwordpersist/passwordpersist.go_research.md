# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist.go

Purpose: defines the password persistence strategy abstraction and helper for connect/create success handling.

Important APIs/types/functions: `Strategy`, `ErrPasswordNotFound`, `ErrUnsupported`, and `OnSuccess`.

Control flow: strategies provide get, persist, and delete methods. `OnSuccess` deletes a stored password when the preceding operation failed and persists the supplied password when it succeeded.

State and persistence behavior: this file owns no storage; concrete strategies may use files, OS keyrings, or no persistence.

Dependencies and integration points: repository connect/create flows use this abstraction through server options and CLI options.

Risks and test signals: `OnSuccess` logs delete failures but returns original operation errors. Tests should exercise failure cleanup and persist error wrapping with fake strategies.
