<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/dirinfo.hpp -->
# sources/user-network-fs/mergerfs/src/dirinfo.hpp

## Purpose

This header defines FUSE file-handle carrier state for mergerfs dirinfo objects, including conversions between typed pointers and integer file handles used by libfuse callbacks. The source was read as a complete 62-line file (1354 bytes).

## Important APIs, Types, and Functions

types: `DirInfo` functions: `DirInfo::to_fh`, `DirInfo::from_fh`, `to_fh`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `assert.hpp`, `fh.hpp`, `base_types.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/dirinfo.hpp -->
