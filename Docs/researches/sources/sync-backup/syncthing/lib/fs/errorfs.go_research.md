# sources/sync-backup/syncthing/lib/fs/errorfs.go

## Purpose
Implements a `Filesystem` that consistently returns a construction error, allowing `NewFilesystem` to return an object even for unrecognized or failed filesystem factories.

## Important APIs, Types, and Functions
`errorFilesystem` stores `err`, `fsType`, and `uri`. It implements all `Filesystem` methods, returning `fs.err` for operations while preserving `Type` and `URI`.

## Control Flow
`NewFilesystem` creates this wrapper when factory lookup or construction fails. Downstream callers can still hold a `Filesystem` but operations fail deterministically.

## State and Persistence Behavior
No filesystem state is mutated. The only state is the stored error and identity.

## Dependencies and Integration Points
Depends on `context`, `time`, and `protocol.PlatformData`. Implements `wrappingFilesystem` as non-unwrappable.

## Risks
Because `Options` returns nil and `SameFile` false, some higher-level code may proceed until first operation rather than failing at construction. This is intentional but can delay error surfacing.

## Test Signals
No direct tests in this subset; behavior is indirectly covered where unknown factories or missing wrappers are exercised.
