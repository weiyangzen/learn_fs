<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.hpp -->
# sources/user-network-fs/mergerfs/src/category.hpp

## Purpose

This file defines category wrappers for mergerfs policy functions, grouping individual FUSE operations into action/create/search policy categories that can be parsed and rendered through config strings. The source was read as a complete 109-line file (2529 bytes).

## Important APIs, Types, and Functions

types: `Base`, `Action`, `Create`, `Search`, `Categories` functions: `from_string`, `to_string`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `tofrom_string.hpp`, `funcs.hpp`, `func.hpp`, `string`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.hpp -->
