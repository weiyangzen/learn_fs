# sources/user-network-fs/rclone/fs/metadata_test.go

## Purpose
`metadata_test.go` validates generic metadata map operations and the external metadata mapper integration.

## Important APIs, types, and functions
Tests cover `fs.Metadata.Set`, `Merge`, `MergeOptions`, `GetMetadataOptions`, `MetadataOption`, and mapper execution configured via `ci.MetadataMapper.Set("go run metadata_mapper_code.go")`. It uses `object.NewMemoryObject` and `mockfs.NewFs`.

## Control flow
Map tests run table-driven nil/empty/non-empty merge cases and option precedence. Mapper tests enable metadata in config, build a destination mock fs and memory object with metadata, then check normal mapped output, mapper error propagation when metadata includes `error`, and option merge overriding object metadata before mapping.

## State and persistence behavior
The tests create in-memory metadata and objects. Mapper tests spawn `go run`, which compiles/runs the helper process, but do not persist repository data. Config is context-local via `fs.AddConfig`.

## Dependencies and integration points
The suite depends on `metadata_mapper_code.go`, memory objects, mock fs, config parsing for `SpaceSepList`, and MIME type detection. It protects copy/upload metadata flows that rely on `GetMetadataOptions`.

## Risks and edge cases
Mapper tests assume `go` is available and that running from the package directory can find `metadata_mapper_code.go`. Exact mapper field checks make tests sensitive to source fs identity, MIME detection, and timestamp formatting.

## Test signals
Coverage is high for local metadata semantics: nil preservation, duplicate key override rules, non-metadata options ignored, external mapper success/failure, and option metadata overriding object metadata.

Source-read signal: reviewed complete local file (157 lines). Functions/methods observed: `TestMetadataSet`, `TestMetadataMerge`, `TestMetadataMergeOptions`, `TestMetadataMapper`.
