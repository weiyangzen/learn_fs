# sources/security-integrity/fscrypt/metadata/constants.go

## Purpose
`constants.go` defines shared key, descriptor, IV, salt, HMAC, and default metadata option constants for fscrypt.

## Important APIs, Types, and Functions
Constants include `PolicyDescriptorLenV1`, `ProtectorDescriptorLen`, `PolicyDescriptorLenV2`, `InternalKeyLen`, `IVLen`, `SaltLen`, `HMACLen`, and `PolicyKeyLen`. Variables include `DefaultOptions` and `DefaultSource`.

## Control Flow
There is no runtime control flow beyond package initialization of default options. Lengths derive from kernel fscrypt constants and SHA-256 size.

## State and Persistence
`DefaultOptions` is a mutable pointer to an `EncryptionOptions` struct, so callers could accidentally mutate shared defaults. The constants define on-disk and kernel-facing metadata sizes.

## Dependencies and Integration Points
Depends on `crypto/sha256` and `golang.org/x/sys/unix`. Used across crypto recovery, keyring validation, metadata checks, policy setup, config defaults, and tests.

## Risks
Because defaults are exported as a pointer, defensive cloning is needed if callers plan to modify options. Kernel constant changes can affect compatibility assumptions.

## Test Signals
Covered indirectly by metadata validation, recovery-code tests, policy tests, and keyring tests that rely on these exact lengths and defaults.
