# sources/sync-backup/syncthing/lib/fs/types.go

## Purpose
Defines filesystem type registration and option extension points.

## Important APIs, Types, and Functions
`FilesystemType`, `Option`, `FilesystemFactory`, global `filesystemFactories`, `filesystemFactoriesMutex`, and `RegisterFilesystemType`.

## Control Flow
Filesystem implementations call `RegisterFilesystemType` in `init`; `NewFilesystem` later looks up the factory under the mutex and invokes it with URI/options.

## State and Persistence Behavior
Maintains a process-global factory map. No disk state.

## Dependencies and Integration Points
`basicfs.go` and `fakefs.go` register built-in types. Plugins/tests can register additional types.

## Risks
Registering the same type overwrites silently. Option equality depends on `String`, so options with parameters must include those parameters in their string representation.

## Test Signals
Exercised indirectly by all `NewFilesystem` tests.
