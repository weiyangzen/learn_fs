# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_kstat.h

## Scope

Defines IBMF kstat data structures and convenience macros for updating client and port statistics.

## Structures

- `ibmf_port_kstat_t` tracks clients registered, registration failures, allocated send/receive WQEs, and WQE allocation failures.
- `ibmf_kstat_t` tracks allocated/active/sent/received messages, active sends/receives, allocated UD destinations and alternate QPs, active callbacks, receive buffers, allocation failures, send packet failures, and RMPP errors.

## Macros

- `IBMF_ADD32_KSTATS()` and `IBMF_SUB32_KSTATS()` adjust a 32-bit client kstat field if client and kstat pointer are valid.
- `IBMF_ADD32_PORT_KSTATS()` and `IBMF_SUB32_PORT_KSTATS()` adjust a 32-bit port kstat field if CI/port kstat pointer is valid.

## Dependencies

- Assumes `kstat_named_t` and illumos kstat structures.
- Macros expect client objects with `ic_kstatp` and CI/port objects with `ci_port_kstatp`.

## Risks And Invariants

- Macros do not acquire locks; callers must hold the relevant kstat mutex where required.
- Counters are plain 32-bit kstat fields and can wrap under sustained long-running activity.
- Field names are macro parameters, so incorrect names fail at compile time but wrong counter choice is a caller responsibility.
