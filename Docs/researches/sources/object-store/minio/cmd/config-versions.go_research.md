# sources/object-store/minio/cmd/config-versions.go

## Purpose
`config-versions.go` defines legacy server config schema types needed for migration to the current `config.Config` representation.

## Important APIs, Types, And Functions
`FileLogger` and `ConsoleLogger` are compatibility structs for older logrus-era config. `serverConfigV33` embeds `quick.Config` and includes version, credentials, region, WORM flag, storage class, notification config, logger config, compression config, OpenID config, legacy OPA policy config, and legacy LDAP config.

## Control Flow
There is no runtime control flow. The structs are populated by JSON/quick config decoding in `config-migrate.go` and then read field-by-field during migration.

## State And Persistence Behavior
The file defines serialized JSON field names for legacy config. It does not persist by itself.

## Dependencies And Integration Points
It depends on `auth`, current/legacy config package types, notification config, storageclass, logger, OpenID, OPA, LDAP, and `quick.Config`. It is tightly coupled to migration code.

## Risks And Test Signals
Changing these structs can break old config decoding. Because only version 33 is represented here with comments about prior changes, migration support for older versions depends on compatibility branches in `config-migrate.go`. No direct tests are in this subset.
