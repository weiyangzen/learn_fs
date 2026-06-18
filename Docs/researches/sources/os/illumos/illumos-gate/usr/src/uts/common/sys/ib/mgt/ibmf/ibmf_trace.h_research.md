# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_trace.h

## Scope

Defines IBMF trace/debug print levels and trace macros.

## APIs And Macros

- Trace levels:
  - `DPRINT_L0`: no messages
  - `DPRINT_L1`: major errors
  - `DPRINT_L2`: minor errors
  - `DPRINT_L3`: general debug
  - `DPRINT_L4`: general trace
- `IBMF_TRACE_0` through `IBMF_TRACE_5` conditionally call `ibmf_dprintf()` when `ibmf_trace_level > 0`.
- `ibmf_dprintf(int l, const char *fmt, ...)` is the underlying debug print function.

## Dependencies

- Relies on an external `ibmf_trace_level` variable defined elsewhere.
- Used by IBMF implementation code for compile-time consistent probe-style trace calls.

## Risks And Invariants

- The first macro arguments preserve a probe-like calling convention, but only format string and selected values are passed to `ibmf_dprintf()`.
- Macros do not wrap bodies in `do { } while (0)`, so use in conditional statements requires care.
- Trace cost is gated only by `ibmf_trace_level > 0`; level filtering is performed by `ibmf_dprintf()` or below.
