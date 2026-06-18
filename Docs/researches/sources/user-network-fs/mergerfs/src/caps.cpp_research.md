<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/caps.cpp -->
# sources/user-network-fs/mergerfs/src/caps.cpp

## Purpose

This file sets up Linux process capabilities needed by mergerfs after startup. It manipulates capability sets and securebits/prctl state so the process can retain required filesystem privileges while dropping others. The source was read as a complete 122-line file (2491 bytes).

## Important APIs, Types, and Functions

types: `__user_cap_header_struct`, `__user_cap_data_struct` functions: `caps::setup`, `capset`, `capget`, `return ::syscall`

## Control Flow

Runtime flow is local to the declared helpers and is invoked by mergerfs startup, configuration handling, branch selection, or filesystem-operation code.

## State and Persistence Behavior

State is local to the declared objects/templates or caller-owned structures; the file itself does not persist data outside normal process memory.

## Dependencies and Integration Points

direct includes: `caps.hpp`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/prctl.h`, `sys/types.h`, `sys/stat.h`, `sys/syscall.h`, `fcntl.h`, `errno.h`, `string.h`, `grp.h`, `linux/capability.h`, `linux/securebits.h`

## Risks and Edge Cases

Risks are primarily integration drift with adjacent mergerfs utilities and insufficient compile coverage for inline/template behavior.

## Test Signals

Compile coverage plus focused unit tests for the exposed helpers and any string/handle conversions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/src/caps.cpp -->
