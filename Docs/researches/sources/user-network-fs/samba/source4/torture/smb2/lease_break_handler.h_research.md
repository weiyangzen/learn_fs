# sources/user-network-fs/samba/source4/torture/smb2/lease_break_handler.h

## Purpose
`lease_break_handler.h` defines the shared state, assertion macros, and reset/helper declarations for SMB2 lease-break torture tests. It is a test-support header, not production protocol logic.

## Important APIs, Types, and Functions
`struct lease_break_info` records the active torture context, last `smb2_lease_break`, receiving `smb2_transport`, ack-skip flag, last `smb2_lease_break_ack`, optional handle to close on break, close response, lease counters, and colocated oplock counters/levels used by combined tests. The external singleton `lease_break_info` is defined in the `.c` file. `torture_lease_handler()` and `torture_wait_for_lease_break()` are declared for test files to install and drive the handler. `torture_reset_lease_break_info()` zeroes the state and reinstalls the current `tctx`.

The macros are the main API surface: `CHECK_LEASE_BREAK`, `CHECK_LEASE_BREAK_ACK`, `CHECK_NO_BREAK`, `CHECK_OPLOCK_BREAK`, `CHECK_BREAK_INFO`, `CHECK_BREAK_INFO_V2`, and NOWAIT variants encode expected lease states, keys, ack behavior, transport routing, and epoch values.

## Control Flow
Tests reset the global state, perform SMB2 creates/writes/closes that may trigger a break, call a macro that invokes `torture_wait_for_lease_break()` when needed, then compare the recorded break and optional ack output. The V2 macros additionally check `new_epoch` and, except for Samba3 targets, the exact transport pointer.

## State and Persistence Behavior
The header models memory-only state owned by the current torture process. Macros mutate state indirectly by waiting for async callbacks and by updating `held_oplock_level` after oplock break checks.

## Dependencies and Integration Points
It depends on `torture/util.h` assertion macros and SMB2 lease/oplock types from including translation units. It is included by lease and multichannel tests, especially where lease break expectations must be written compactly.

## Risks and Edge Cases
The macros assume local variables such as `tctx` exist in scope for several checks. Key checks only validate the two 64-bit words filled by Samba test helpers (`key` and bitwise inverse). The global structure combines lease and oplock fields, so callers must reset it before each scenario to avoid stale counts.

## Test Signals
The header is itself test instrumentation. Its signal is compile-time integration plus repeated use by lease and multichannel suites to enforce state transitions, ack payloads, no-break windows, transport routing, and epoch increments.
