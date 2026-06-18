# sources/object-store/minio/cmd/config-current_test.go

## Purpose
`config-current_test.go` verifies basic server configuration initialization and region mutation through MinIO's current config map.

## Important APIs, Types, And Functions
`TestServerConfig` uses `prepareFS`, `newTestConfig`, `globalServerConfig`, `globalSite`, `config.SetRegion`, and `config.LookupSite`.

## Control Flow
The test creates a filesystem-backed object layer, initializes test config with the default MinIO region, asserts `globalSite.Region()`, mutates the region in `globalServerConfig`, and verifies `config.LookupSite` returns the new region.

## State And Persistence Behavior
The test creates and removes a temporary FS backend. It mutates package globals (`globalServerConfig`, `globalSite`) through normal test initialization paths.

## Dependencies And Integration Points
It integrates with filesystem object-layer test setup, current config defaults, site/region config helpers, and the config load path used by startup.

## Risks And Test Signals
This is a smoke test, not comprehensive config validation. It does not exercise dynamic subsystem application, env merging, encrypted config, migration, or external target validation. It is still a useful signal that default config creation and site region fields remain compatible.
