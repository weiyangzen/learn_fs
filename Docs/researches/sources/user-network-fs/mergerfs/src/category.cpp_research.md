<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.cpp -->
# sources/user-network-fs/mergerfs/src/category.cpp

## Purpose

This file defines category wrappers for mergerfs policy functions, grouping individual FUSE operations into action/create/search policy categories that can be parsed and rendered through config strings. The source was read as a complete 49-line file (1260 bytes).

## Important APIs, Types, and Functions

functions: `Category::Base::from_string`, `Category::Base::to_string`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `category.hpp`, `errno.hpp`, `str.hpp`, `string`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/category.cpp -->
