<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_moveonenospc.hpp -->
# sources/user-network-fs/mergerfs/src/config_moveonenospc.hpp

## Purpose

This header defines the mergerfs config adapter for move-on-ENOSPC handling, either false or a create policy such as the default pfrd policy. It contributes a `ToFromString`-compatible type or enum used by the global `Config` registry. The source was read as a complete 44-line file (1224 bytes).

## Important APIs, Types, and Functions

types: `MoveOnENOSPC` functions: `from_string`, `to_string` recognized/config strings include: `policy.hpp`, `policies.hpp`, `tofrom_string.hpp`

## Control Flow

Control flow is driven by `Config::get`, `Config::set`, config-file parsing, and the control-xattr interface. The registry locates the option adapter, checks read-only state after initialization, then calls `from_string`; reads call `to_string`.

## State and Persistence Behavior

The adapter stores small in-memory option state or mutates a shared subsystem such as `fuse_cfg`, debug logging, inode calculation, or ioprio. Values persist for the life of the mounted process unless changed through a writable runtime config path.

## Dependencies and Integration Points

direct includes: `policy.hpp`, `policies.hpp`, `tofrom_string.hpp`, `string`

## Risks and Edge Cases

Invalid string handling must return stable negative errno values without partially updating state. Enum string drift can break documented config values, and adapters mutating shared subsystems need ordering tests with runtime config writes.

## Test Signals

Config round-trip tests for every documented string, invalid-value errno tests, and integration tests through `Config::set`/`Config::get` and the runtime xattr path.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/config_moveonenospc.hpp -->
