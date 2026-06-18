<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.cpp -->
# sources/user-network-fs/mergerfs/src/branch.cpp

## Purpose

This file implements or declares a single mergerfs branch record: backing path, access mode, and min-free-space value. Branch records are the units selected by policy code and exposed through the branch configuration string. The source was read as a complete 100-line file (2116 bytes).

## Important APIs, Types, and Functions

functions: `Branch::Branch`, `Branch::to_string`, `Branch::set_minfreespace`, `Branch::minfreespace`, `Branch::ro`, `Branch::nc`, `Branch::ro_or_nc` recognized/config strings include: `branch.hpp`, `num.hpp`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `branch.hpp`, `num.hpp`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/branch.cpp -->
