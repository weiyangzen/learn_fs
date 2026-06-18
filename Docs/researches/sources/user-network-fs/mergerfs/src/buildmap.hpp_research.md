<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/buildmap.hpp -->
# sources/user-network-fs/mergerfs/src/buildmap.hpp

## Purpose

This template header provides a small fluent builder wrapper for constructing standard `map` containers and returning a sorted collection at the end of chained insertions. The source was read as a complete 48-line file (1261 bytes).

## Important APIs, Types, and Functions

types: `buildmap`

## Control Flow

The file is mostly compile-time declarations/templates or inline helpers; callers provide the runtime flow through mergerfs config, policy, or FUSE operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `algorithm`, `map`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/buildmap.hpp -->
