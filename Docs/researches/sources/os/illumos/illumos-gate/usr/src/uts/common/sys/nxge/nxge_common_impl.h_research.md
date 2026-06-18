# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_common_impl.h

## Purpose

`nxge/nxge_common_impl.h` provides implementation-side OS abstraction macros, debug bit definitions, PIO/register access helpers, FMA wrappers, and tracing-aware register read/write macros for the nxge driver and NPI layer.

## Main Interfaces

`NPI_REGH()` and `NPI_REGP()` extract register handle and mapped register pointer from an NPI handle. `__NXGE_STATIC` and `__NXGE_INLINE` expand differently when DMA/TXC debug builds need externally visible helpers.

The header defines a large `nxge_debug_level` bitmask space, including subsystem bits for metadata, RX, TX, OBP, VPD, DDI, memory, SAP, ioctl, module, DMA, STREAMS, interrupts, system errors, kstats, PCS/MII/MIF/FCRAM/MAC/IPP, secondary paths, NDD, TCAM, config, virtualization, HIO, notes, error control, and dump-always. NPI debug flags cover RDC, TDC, TXC, IPP, PCS/MAC/ZCP/TCAM/FCRAM/FFLP/VIR/PIO/VIO/register/control/error areas.

It includes DDI and Ethernet headers, maps NXGE mutex/rwlock/allocation/delay macros to illumos kernel primitives, and typedefs OS-facing types for mutexes, rwlocks, devinfo, interrupt cookies, access handles, DMA handles, and free routines.

PIO macros wrap `ddi_get*()`/`ddi_put*()` for general device offsets, NPI register offsets, and memory-style mapped register access. Some 64-bit NPI access macros cast offsets on i386.

FMA macros wrap DDI service/fault constants and fault-report/check helpers. Register read/write macros optionally record trace/show output under `REG_TRACE` or `REG_SHOW`.

## Runtime Use

Driver code uses these macros to centralize register I/O, synchronization, memory allocation, fault reporting, debug logging, and trace instrumentation. Build flags can compile in additional tracing or expose static functions for debugging.

## Dependencies

Includes `sys/types.h`, `sys/ddi.h`, `sys/sunddi.h`, `sys/dditypes.h`, and `sys/ethernet.h`. Depends on nxge and NPI types defined by surrounding driver headers.

## Risks and Invariants

Register access macros evaluate arguments directly and perform typed pointer arithmetic on mapped register bases; incorrect offsets or widths can cause hardware faults or corrupt device state.

`NXGE_PIO_WRITE16` appears to call `ddi_get16()` with a write-like argument list instead of `ddi_put16()`. If used, that macro would be wrong or fail to compile; it may be unused or masked by other access paths.

Debug and trace macros can materially change visibility and side effects. Code relying on `__NXGE_STATIC` behavior must account for debug builds.

FMA wrappers assume `nxgep` has valid `dip` and register handles; using them during partial attach/detach needs state checks.
