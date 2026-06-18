# sources/security-integrity/fscrypt/actions/protector.go

## Purpose
Implements protector lifecycle. Protectors wrap policy keys and are themselves protected by login passphrases, custom passphrases, or raw keys.

## APIs, Types, and Control Flow
Exports include `LoginProtectorMountpoint`, protector naming errors, `Protector`, `CreateProtector`, `GetProtector`, `GetProtectorFromOption`, and methods for descriptor, destroy, revert, unlock, lock, and rewrap. `CreateProtector` validates naming rules, checks duplicate names or login protectors, populates source-specific metadata such as UID, salt, and hashing costs, generates a random internal key, computes a v1 descriptor, wraps it using `Rewrap`, and persists metadata.

`Unlock` calls `unwrapProtectorKey` only when the in-memory key is absent. `Lock` wipes the key and nils it. `Rewrap` requires an unlocked internal key, derives or reads the wrapping key via `getWrappingKey`, wraps the internal key, persists with `Mount.AddProtector`, and restores the old wrapped key if persistence fails.

## State, Dependencies, and Integration
Protector metadata is persisted in `.fscrypt/protectors` through `filesystem.Mount`. Passphrase protectors depend on config hashing costs and random salt. Login protectors embed target UID and are usually stored on `LoginProtectorMountpoint` by command-layer helpers. Crypto dependencies include random key generation, descriptors, wrapping, and key wiping.

## Risks and Test Signals
`Lock` assumes `protector.key.Wipe()` is safe when the key is nil. Naming and duplicate checks rely on readable existing metadata. Failed callback or wrapping paths must wipe generated keys and avoid partially persisted protectors. Tests cover creation and callback error propagation, while CLI tests cover names, login protectors, raw keys, and passphrase changes.
