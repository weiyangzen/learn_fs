# sources/security-integrity/gocryptfs/internal/configfile/scrypt.go

Purpose: This file implements the scrypt KDF parameter object used to derive config key-encryption keys from passwords.

Important APIs and types: `ScryptKDF` stores salt and parameters. `NewScryptKDF(logN)` creates fresh random salt and configured N/r/p values. `DeriveKey(password)` runs scrypt to produce a key for master-key encryption.

Control flow and state: Salt and cost parameters persist in `gocryptfs.conf`; derived keys are runtime secrets that callers wipe after use. Validation bounds on logN are enforced by config validation and tests.

Dependencies and integration points: Used by `ConfFile.EncryptKey`, `ConfFile.DecryptMasterKey`, init, mount, passwd, and tests.

Risks and test signals: Weak or invalid KDF parameters reduce password security or cause resource exhaustion. Signals include parameter validation tests, wrong-password failures, and minimum runtime checks.
