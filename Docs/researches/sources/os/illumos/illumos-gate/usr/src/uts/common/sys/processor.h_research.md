# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/processor.h

## Purpose
Defines public processor identifiers, processor online/state flags, processor info layout, CPU binding constants, and user/kernel processor system-call interfaces.

## Main Interfaces
- Types:
  - `lgrpid_t`
  - `processorid_t`
  - `chipid_t`
- `p_online(2)`/processor state constants:
  - `P_OFFLINE`, `P_ONLINE`, `P_STATUS`, `P_FAULTED`, `P_POWEROFF`, `P_NOINTR`, `P_SPARE`, `P_DISABLED`, `P_BAD`, `P_FORCED`
- State strings:
  - `PS_OFFLINE`, `PS_ONLINE`, `PS_FAULTED`, `PS_POWEROFF`, `PS_NOINTR`, `PS_SPARE`, `PS_DISABLED`
- `processor_info_t`: state, CPU type string, FPU type string, and clock MHz.
- Binding constants:
  - `PBIND_NONE`
  - `PBIND_QUERY`
  - `PBIND_HARD`
  - `PBIND_SOFT`
  - `PBIND_QUERY_TYPE`
- Sentinel:
  - `P_ALL_SIBLINGS`
- User APIs:
  - `p_online()`
  - `processor_info()`
  - `processor_bind()`
  - `getcpuid()`
  - `gethomelgroup()`
- Kernel APIs:
  - `p_online_internal()`
  - `p_online_internal_locked()`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/procset.h`. The header notes that public `P_*` flags are not for inspecting in-kernel CPU state; kernel code should use `sys/cpuvar.h`.

## Research Notes
`processor_info_t` is explicitly ABI-stable and should not be modified. String fields are guaranteed NUL-terminated.
