<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.hpp -->
# sources/user-network-fs/mergerfs/src/branch.hpp

## Purpose

This file implements or declares a single mergerfs branch record: backing path, access mode, and min-free-space value. Branch records are the units selected by policy code and exposed through the branch configuration string. The source was read as a complete 67-line file (1526 bytes).

## Important APIs, Types, and Functions

types: `Branch`, `Mode`, `class` functions: `ro`, `nc`, `ro_or_nc`, `to_string`, `minfreespace`, `set_minfreespace` enum values: `Mode` (RO, RW, NC)

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `base_types.h`, `strvec.hpp`, `fs_path.hpp`, `cstdint`, `memory`, `optional`, `string`, `vector`, `variant`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.hpp -->
