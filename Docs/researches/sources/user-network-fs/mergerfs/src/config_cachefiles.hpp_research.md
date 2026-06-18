<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_cachefiles.hpp -->
# sources/user-network-fs/mergerfs/src/config_cachefiles.hpp

## Purpose

This header defines the mergerfs config adapter for cache file behavior: `off`, `partial`, `full`, `auto-full`, and `per-process`. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 33-line file (980 bytes).

## Important APIs, Types, and Functions

types: `CacheFilesEnum`, `class` enum values: `CacheFilesEnum` (OFF, PARTIAL, FULL, AUTO_FULL, PER_PROCESS) recognized/config strings include: `enum.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `enum.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_cachefiles.hpp -->
