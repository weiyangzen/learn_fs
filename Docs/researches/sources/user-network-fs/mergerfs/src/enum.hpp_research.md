<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/enum.hpp -->
# sources/user-network-fs/mergerfs/src/enum.hpp

## Purpose

This utility file supports mergerfs parsing, portability, or error handling infrastructure shared by config and filesystem helpers. The source was read as a complete 81-line file (1556 bytes).

## Important APIs, Types, and Functions

types: `Enum` functions: `to_string`, `from_string`, `to_int`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `string`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/enum.hpp -->
