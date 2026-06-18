# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_file.go

Purpose: stores repository passwords in a sidecar file next to the config file.

Important APIs/types/functions: `File`, `filePasswordStorage`, `GetPassword`, `PersistPassword`, `DeletePassword`, `passwordFileName`, and `passwordFileMode`.

Control flow: password values are base64-encoded into `<config>.kopia-password`; reads translate missing files to `ErrPasswordNotFound` and invalid base64 to a wrapped error; delete ignores missing files.

State and persistence behavior: persists plaintext-equivalent base64 data in a `0600` file.

Dependencies and integration points: fallback or configured persistence strategy for repository passwords.

Risks and test signals: base64 is not encryption, so file permissions are security-critical. Tests should cover mode, invalid contents, missing file, and delete idempotence.
