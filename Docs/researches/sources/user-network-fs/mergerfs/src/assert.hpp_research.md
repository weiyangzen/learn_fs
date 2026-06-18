<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/assert.hpp -->
# sources/user-network-fs/mergerfs/src/assert.hpp

## Purpose

This header defines compile-time and runtime assertion helpers used by mergerfs internals, including `STATIC_ASSERT`, array-length assertions, and optional null-pointer diagnostics before calling `assert`. The source was read as a complete 56-line file (1846 bytes).

## Important APIs, Types, and Functions

types: `StaticAssert` macros: `STATIC_ASSERT`, `STATIC_ARRAYLENGTH_ASSERT`, `ASSERT_NOT_NULL`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `cassert`, `iostream`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/assert.hpp -->
