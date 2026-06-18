# sources/object-store/minio/cmd/config-migrate.go

## Purpose
`config-migrate.go` loads legacy MinIO configuration locations and schemas, migrates older `serverConfigV33` JSON into the current `config.Config`, and initializes new config when no readable config exists.

## Important APIs, Types, And Functions
`Save` and `Load` wrap `quick.SaveConfig`/`quick.LoadConfig` with `globalEtcdClient`. `readConfigWithoutMigrate` checks legacy filesystem paths, deprecated paths, and `.minio.sys/config/config.json`; decrypts object-stored config; tries current `readServerConfig`; falls back to legacy JSON; applies version-specific migrations from 29 through 33; preserves old credentials when env credentials are absent; and copies region, storage class, logger/audit, LDAP, OPA, compression, and notification settings into a new current config.

## Control Flow
The loader first tries quick config paths, then object-store config. Missing config creates and saves a fresh current config. If current unmarshalling succeeds, it returns merged current config. If not, legacy schema unmarshalling drives migration and returns a current map without writing it in this function.

## State And Persistence Behavior
Fresh initialization persists config via `saveServerConfig`. Migration updates `globalActiveCred` when appropriate but otherwise returns the migrated config to callers. It may read from filesystem, etcd, or `.minio.sys`.

## Dependencies And Integration Points
It integrates with config-dir paths, quick config storage, object-store config helpers, config encryption/decryption, legacy notification target structs, logger config setters, LDAP/OpenID/OPA/compression/storageclass packages, and global credential state.

## Risks And Test Signals
Risks include lossy migration if a legacy field has no current setter, silent reinitialization on unparsable legacy JSON, and mixed legacy/current locations. No direct migration tests are in this subset; coverage depends on broader config compatibility tests.
