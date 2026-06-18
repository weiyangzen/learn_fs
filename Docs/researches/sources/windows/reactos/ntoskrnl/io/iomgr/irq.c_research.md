# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/irq.c

## Role

`irq.c` implements I/O-manager wrappers for kernel interrupt objects. It maps the legacy `IoConnectInterrupt()` API and the newer `IoConnectInterruptEx()`/`IoDisconnectInterruptEx()` forms onto kernel interrupt initialization and connection primitives.

## Main entry points and behavior

- `IoConnectInterrupt()` counts CPUs in `ProcessorEnableMask & KeActiveProcessors`, allocates one `IO_INTERRUPT` wrapper plus extra `KINTERRUPT` storage for additional processors, initializes a caller-provided or internal spin lock, initializes one interrupt object per enabled processor, and connects each with `KeConnectInterrupt()` (lines 21-135).
- If connection fails on the first processor, the wrapper allocation is freed; if failure occurs after the first connection, `IoDisconnectInterrupt()` unwinds all connected interrupts (lines 101-118).
- `IoDisconnectInterrupt()` recovers the owning `IO_INTERRUPT` from the first interrupt object, disconnects the first and any stored additional interrupts, and frees the wrapper with `TAG_IO_INTERRUPT` (lines 137-170).
- `IopConnectInterruptExFullySpecific()` adapts `CONNECT_FULLY_SPECIFIED` parameters to `IoConnectInterrupt()` and logs failure (lines 172-195).
- `IoConnectInterruptEx()` supports fully specified and fully specified group connections by using the same fallback. Message-based and line-based forms only log `FIXME` and return success (lines 197-220).
- `IoDisconnectInterruptEx()` currently only disconnects `ConnectionContext.InterruptObject` if present (lines 222-232).

## Data and synchronization

The per-connection wrapper owns an internal spin lock when the caller did not provide one. The additional interrupt object pointers are stored in `IoInterrupt->Interrupt[]`, while the first object is embedded as `FirstInterrupt`.

## Implementation gaps and risks

- `CONNECT_MESSAGE_BASED` and `CONNECT_LINE_BASED` are unimplemented but `IoConnectInterruptEx()` falls through to `STATUS_SUCCESS`, which can mislead callers expecting a connected interrupt (lines 211-219).
- `CONNECT_FULLY_SPECIFIED_GROUP` ignores processor groups and reuses the non-group path (lines 208-210).
- The allocation size uses `(Count - 1) * sizeof(KINTERRUPT) + sizeof(IO_INTERRUPT)` while subsequent code also stores pointers in `IoInterrupt->Interrupt[(UCHAR)Count]`; correctness depends on the exact `IO_INTERRUPT` layout defined elsewhere (lines 59-63, 127-129).
