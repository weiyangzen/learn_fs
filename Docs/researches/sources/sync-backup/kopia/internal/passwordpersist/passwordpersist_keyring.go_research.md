# sources/sync-backup/kopia/internal/passwordpersist/passwordpersist_keyring.go

Purpose: stores repository passwords in the operating-system keyring.

Important APIs/types/functions: `Keyring`, `keyringStrategy`, `GetPassword`, `PersistPassword`, `DeletePassword`, `getKeyringItemID`, and `keyringUsername`.

Control flow: derives a stable keyring item ID from config basename plus SHA-256 prefix, uses current OS user as username, normalizes Windows domain names, and maps keyring errors to Kopia persistence errors.

State and persistence behavior: secrets persist in OS keychain/keyring; no in-process cache.

Dependencies and integration points: uses `github.com/zalando/go-keyring`, `os/user`, and repository config paths.

Risks and test signals: keyring availability and locked keyrings vary by platform/session. Tests need mocks or integration opt-ins for unsupported, not found, save, delete, and username normalization.
