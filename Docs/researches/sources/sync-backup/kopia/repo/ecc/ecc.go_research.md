# sources/sync-backup/kopia/repo/ecc/ecc.go

## Purpose
Provides the registry and factory interface for ECC algorithms, exposing ECC implementations as `encryption.Encryptor` instances so they can be composed with content encryption.

## Important APIs, Types, And Functions
`CreateECCFunc` is a factory signature. `RegisterAlgorithm` adds factories to the package-global map. `SupportedAlgorithms` returns sorted registered names. `CreateAlgorithm` looks up and creates an algorithm from `Options`. `Parameters` captures format-layer ECC fields, and `CreateEncryptor` converts those parameters to `Options`.

## Control Flow
Algorithms register themselves in `init` functions. Creation is a map lookup followed by factory invocation. Supported algorithm listing iterates the map and sorts names for stable output.

## State And Persistence
The only state is the in-memory package-global registry. There is no persistence.

## Dependencies And Integration Points
Depends on `repo/encryption` for the shared encryptor interface. `format.NewFormattingOptionsProvider` calls `ecc.CreateEncryptor` when a repository format enables ECC.

## Risks And Edge Cases
Unknown algorithm names return an error. Registry mutation is not synchronized, but expected use is init-time registration before concurrent access. Since ECC is modeled as encryption, callers must understand it may add integrity/recovery data rather than secrecy.

## Test Signals
ECC creation and behavior are covered indirectly by `ecc_rs_crc_test.go` and `ecc_utils_test.go`, which use `CreateAlgorithm`.
