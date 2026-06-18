# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/qlc/ql_debug.h

This header defines QLogic qlc debug and extended logging prototypes/macros.

Key contents:
- Debug function prototypes:
  - `ql_dump_buffer`
  - `ql_el_msg`
  - `ql_dbg_msg`
  - `ql_flash_errlog`
  - `ql_dump_el_trace_buffer`
- Conditional `QL_DEBUG_ROUTINES` and message prefix macros based on `QL_DEBUG`.
- Global extended-log and trace-buffer locking macros.
- Extended log macro `EL()` and direct `cmn_err()` error macros `ER()`/`ERV()`.
- Trace buffer reservation and debug stack-depth constants.
- Debug levels 1 through 16, each conditionally mapping `QL_PRINT_N` and `QL_DUMP_N` to debug routines when the relevant `QL_DEBUG` bit is enabled, or to no-ops otherwise.
- Level 2 is enabled for any nonzero lower 16 bits of `QL_DEBUG` through `QL_DEBUG_ROUTINES`; level 9 is enabled for `QL_DEBUG & 0x104`.

Dependencies:
- Uses `ql_adapter_state_t`, `ql_global_el_mutex`, `cmn_err`, `CE_CONT`, and mutex primitives from including context.

Research notes:
- This is compile-time controlled instrumentation; when debug bits are disabled most macros compile away.
- The file provides both per-adapter debug logging and global extended logging trace-buffer support.
