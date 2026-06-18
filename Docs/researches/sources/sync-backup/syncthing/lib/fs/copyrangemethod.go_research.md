# sources/sync-backup/syncthing/lib/fs/copyrangemethod.go

## Purpose
Defines the selectable copy-range strategies used by Syncthing to copy file ranges, including clone/offload-capable system calls and the standard fallback.

## Important APIs, Types, and Functions
`CopyRangeMethod` enum values: `Standard`, `Ioctl`, `CopyFileRange`, `SendFile`, `DuplicateExtents`, and `AllWithFallback`. `String` renders stable configuration/metric names.

## Control Flow
No copy logic here; methods are registered in platform-specific files and dispatched by `CopyRange`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Integrated with `filesystem_copy_range.go` registry and platform copy implementations.

## Risks
Unknown enum values stringify as `unknown`, so configuration validation must happen elsewhere if strictness is required.

## Test Signals
`filesystem_copy_range_test.go` iterates registered methods and uses `String` in subtest names.
