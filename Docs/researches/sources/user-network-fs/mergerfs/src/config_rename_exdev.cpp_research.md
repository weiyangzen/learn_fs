<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_rename_exdev.cpp -->
# sources/user-network-fs/mergerfs/src/config_rename_exdev.cpp

## Purpose

This implementation parses and formats the mergerfs config option for cross-device rename behavior: passthrough or symlink fallback modes. It is called through the `Config` registry and runtime xattr/config-file paths. The source was read as a complete 54-line file (1519 bytes).

## Important APIs, Types, and Functions

functions: `RenameEXDEV::to_string`, `RenameEXDEV::from_string` recognized/config strings include: `config_rename_exdev.hpp`, `ef.hpp`, `errno.hpp`, `passthrough`, `rel-symlink`, `abs-symlink`, `invalid`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `config_rename_exdev.hpp`, `ef.hpp`, `errno.hpp`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_rename_exdev.cpp -->
