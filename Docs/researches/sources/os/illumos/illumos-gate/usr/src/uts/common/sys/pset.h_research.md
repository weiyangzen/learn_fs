# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pset.h

## Role

`pset.h` defines the processor-set user/kernel ABI: the `psetid_t` type, special processor-set identifiers, processor-set types, userland library prototypes, system-call subcodes, and attribute flags.

## Key Interfaces

The special IDs allow callers to express nonliteral targets:
- `PS_NONE`, `PS_QUERY`, `PS_MYID`
- `PS_SOFT`, `PS_HARD`
- `PS_QUERY_TYPE`

Processor-set types are `PS_SYSTEM` and `PS_PRIVATE`.

Outside the kernel, the header declares:
- `pset_create()`, `pset_destroy()`
- `pset_assign()`, `pset_info()`, `pset_list()`
- `pset_bind()`, `pset_bind_lwp()`
- `pset_getloadavg()`
- `pset_setattr()`, `pset_getattr()`

The syscall subcodes map these operations to numeric dispatch values, including forced assignment and LWP binding. The only attribute bit defined here is `PSET_NOESCAPE`.

## Research Notes

This is a compact ABI header. The critical stability surface is the numeric values of special IDs, syscall subcodes, and `PSET_NOESCAPE`, because userland and kernel dispatch logic must agree exactly.
