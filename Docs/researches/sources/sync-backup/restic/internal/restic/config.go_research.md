
# sources/sync-backup/restic/internal/restic/config.go

Purpose: defines repository configuration and helpers to create, load, validate, and save it.

`Config` stores repository format version, repository ID, and chunker polynomial. Constants define min, max, and stable repo versions. `CreateConfig` generates a random chunker polynomial and repository ID. `LoadConfig` loads JSON through encrypted unpacked storage, validates version range, and optionally checks polynomial irreducibility. `SaveConfig` writes config JSON as a `ConfigFile` through `SaveJSONUnpacked`. `TestDisableCheckPolynomial` is a test hook guarded by `sync.Once`.

State is persisted as the repository config file; unlike other unpacked files it has the null ID and is bootstrapped during repository open. Integration points include repository initialization, key search, upgrade, chunking, and tests. Risks include invalid polynomial checks, version compatibility, global test hook leakage, and config load failure after key decryption. Tests check save/load round-trip and helper behavior.
