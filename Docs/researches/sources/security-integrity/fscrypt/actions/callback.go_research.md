# sources/security-integrity/fscrypt/actions/callback.go

Purpose: defines callback interfaces used by fscrypt actions to obtain keys from callers and choose protectors for unlocking policies.

Important APIs/types/functions: `ProtectorInfo` wraps `metadata.ProtectorData` and exposes read-only accessors `Descriptor`, `Source`, `Name`, and `UID`. `KeyFunc` asks the caller for a passphrase or raw 256-bit key, with a retry flag. `getWrappingKey` returns raw keys directly for `SourceType_raw_key` and otherwise hashes passphrases with `crypto.PassphraseHash`. `unwrapProtectorKey` loops until `crypto.Unwrap` succeeds, the callback errors, or a non-auth error occurs. `ProtectorOption` augments `ProtectorInfo` with `LinkedMount` and `LoadError`. `OptionFunc` lets callers choose a protector option by index.

Control flow: unwrapping starts with `retry=false`, obtains a wrapping key, attempts unwrap, wipes the wrapping key, returns protector key on success, sets retry on `crypto.ErrBadAuth`, and propagates other errors. Passphrase inputs are wiped after hashing.

State and persistence: no persistence. Sensitive callback-returned keys are expected to be wiped by consumers; this file explicitly wipes passphrases after hashing and wrapping keys after unwrap.

Dependencies and integration points: depends on `crypto`, `filesystem`, `metadata`, `github.com/pkg/errors`, and `log`. It is a core action-layer abstraction between UI/CLI prompting and metadata/key unwrapping.

Risks: raw key sources trust the callback to return correctly sized high-entropy keys. `unwrapProtectorKey` can loop indefinitely if the callback keeps returning wrong keys without error. Logging protector descriptors may be useful for diagnostics but is metadata exposure.

Test signals: no direct tests in this subset, but behavior should be covered by action tests that simulate wrong passphrase retry, callback errors, raw key sources, passphrase wiping, and option selection.
