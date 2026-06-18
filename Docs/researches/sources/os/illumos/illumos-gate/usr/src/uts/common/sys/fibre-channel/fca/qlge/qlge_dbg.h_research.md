# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlge/qlge_dbg.h

## Role

`qlge_dbg.h` defines debug-level flags and conditional debug/core-dump macros for the `qlge` Ethernet driver.

## Major Definitions

Debug levels include flags for:
- NVRAM/register/PCI operations.
- Initialization.
- GLD.
- Mailbox and flash.
- RX, RX rings, TX, statistics, and interrupts.

If `QL_DUMPFW` is defined, `QLA_CORE_DUMP` and `QLA_DUMP_CRASH_RECORD` call the corresponding dump functions; otherwise they compile away.

If `QL_DEBUG` is enabled, macros route debug printing and buffer/descriptor dumps through `ql_printf`, `ql_dump_buf`, `ql_dump_req_pkt`, `ql_dump_cqicb`, and `ql_dump_wqicb` when the adapter’s `ql_dbgprnt` mask includes the requested level. If `QL_DEBUG` is disabled, these macros compile to no-ops.

The file also defines logging severity marker strings:
- `QL_BANG`
- `QL_QUESTION`
- `QL_CAROT`

## Integration Notes

This header depends on `qlge_t` fields and debug helper functions declared elsewhere, especially in `qlge.h`. It is deliberately macro-heavy so debug code can be compiled out when not enabled.
