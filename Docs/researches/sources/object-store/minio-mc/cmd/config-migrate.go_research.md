# sources/object-store/minio-mc/cmd/config-migrate.go

## Purpose

`config-migrate.go` upgrades mc config files from older schema versions to the current v10 alias format. It preserves user credentials/aliases where possible while applying historical defaults and schema renames.

## Important APIs, Control Flow, And State

`migrateConfig` runs each migration step in order, with every step first loading `ConfigAnyVersion` and returning unless the current version exactly matches its source version. V1 to V1.0.1 adds example localhost, loopback, and AWS entries. V1.0.1 to V2 switches to integer versioning. V2 to V3 changes host config JSON tags. V3 to V4 adds API signature defaults. V4 to V5 renames `Signature` to `API`. V5 to V6 adds GCS defaults and normalizes AWS glob patterns. V6 to V7 drops the separate alias map and converts host entries into named hosts, preserving old alias names when possible and assigning `cloudN` otherwise. V7 to V8 removes deprecated play/dl aliases. V8 to V9 adds virtual lookup defaulting to auto. V9 to V10 renames `hosts` to `aliases` and maps lookup `dns/path/auto` to path `off/on/auto`.

## State, Dependencies, Integration, Risks, And Tests

The file persists changes to `mustGetMcConfigPath()` using `quick.NewConfig(...).Save`, logs successful migrations, and fatals on load/save failures. Dependencies include all historical config structs and host conversion types. Risks are ordered migration coupling, alias collisions during V6 to V7, default entries overriding user expectations, and inability to continue after partially written configs. Tests are not in this subset; high-value signals would be fixture migrations for every version and idempotency checks when current version is not in scope.
