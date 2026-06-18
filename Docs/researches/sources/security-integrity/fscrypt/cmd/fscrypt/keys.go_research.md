# sources/security-integrity/fscrypt/cmd/fscrypt/keys.go

## Purpose
Collects passphrases and raw keys from terminals, stdin, files, and PAM validation, then exposes them as `actions.KeyFunc` callbacks.

## APIs, Types, and Control Flow
Defines `existingKeyFn`, `oldExistingKeyFn`, `createKeyFn`, and `newCreateKeyFn` from `makeKeyFunc`. `passphraseReader.Read` reads stdin byte-by-byte, handles newline EOF, Ctrl-C/Ctrl-D cancellation, and backspace. `getPassphraseKey` disables terminal echo using raw mode when stdin is a terminal, prints prompts unless quiet, and creates a `crypto.Key`. `makeRawKey` reads 32-byte raw keys from stdin in non-interactive mode or from a prompted/flagged file with length validation. `makeKeyFunc` handles retry semantics, prompts based on protector source, confirms custom passphrases, validates login passphrases through PAM when creating, and rejects raw keys in passphrase-only flows.

## State, Dependencies, and Integration
Uses global flags for quiet mode and key file path. Integrates with `actions` protector/policy unlock and creation, `pam.IsUserLoginToken`, `crypto.Key` memory handling, and `metadata.InternalKeyLen`.

## Risks and Test Signals
Terminal raw mode restoration is essential. Quiet retry returns `ErrWrongKey` rather than prompting. Raw key length is strict. CLI tests cover custom, login, raw-key, and passphrase-change flows.
