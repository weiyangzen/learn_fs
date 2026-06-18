# sources/user-network-fs/rclone/backend/compress/unknown_handler.go

## Purpose
This file defines a defensive handler for unknown compression modes. It returns explicit errors for operations that require a known algorithm.

## Important APIs, types, and functions
`unknownModeHandler` implements the full `compressionModeHandler` interface. `isCompressible`, `openGetReadCloser`, `putCompress`, and `putUncompressGetNewMetadata` all return errors that include the unknown mode where possible. `newObjectGetOriginalSize` returns zero, `processFileNameGetFileExtension` returns empty, and `newMetadata` returns nil.

## Control flow
If selected, any attempt to check compressibility, open compressed data, upload compressed data, or produce metadata should fail quickly. The handler does not attempt compatibility behavior or migration.

## State and persistence behavior
It does not create or interpret persistent compression metadata beyond returning zero size from `newObjectGetOriginalSize`. No data should be written successfully through this handler.

## Dependencies and integration points
It depends on rclone `fs`, `chunkedreader`, and the package's `Object`/`Fs` types. However, `compress.go` currently maps all unknown mode strings to `Uncompressed`, and the switch's default branch is therefore not reachable through `compressionModeFromName` as written.

## Risks and edge cases
The apparent unreachable state means typoed config values do not get this clearer unknown-mode behavior. If future code passes a truly unknown integer mode, `newObjectGetOriginalSize` returning zero could cause misleading object-name lookups before errors occur elsewhere. The handler methods are mostly stubs and should not be treated as a migration path for unknown stored metadata modes.

## Test signals
There are no tests for this handler or for invalid compression mode config behavior.
