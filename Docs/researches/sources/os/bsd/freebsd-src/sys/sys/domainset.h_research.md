# File Research: sources/os/bsd/freebsd-src/sys/sys/domainset.h

## Purpose
Defines NUMA memory-domain bitset operations, domainset policies, kernel domainset structures, and userland cpuset-domain APIs.

## Main Elements
- `DOMAINSET_*` macros wrap generic bitset operations over `DOMAINSET_SETSIZE`.
- `DOMAINSETBUFSIZ` sizes textual domainset formatting with policy and max domain values.
- Policies: invalid, round-robin, first-touch, prefer, interleave.
- Kernel `struct domainset` stores allowed mask, policy, preferred domain, count, and iteration order.
- Predefined domainsets: first-touch, interleave, fixed, prefer, round-robin.
- Kernel APIs initialize, create/intern, remove empty VM domains, and populate/validate domainsets.
- Userland APIs: `cpuset_getdomain()` and `cpuset_setdomain()`.

## Dependencies And Integration
Works with cpuset, VM memory domains, jails/process affinity, and `kern_cpuset.c`.

## Risk Notes
Policy/mask validation is crucial: empty or out-of-range domain masks can break allocation policy. `domainid_t` width changes with `MAXMEMDOM`.
