# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm_usage.h

## Role

`vm_usage.h` defines the `getvmusage()` interface for aggregating resident memory and swap usage by system, zone, project, task, real user, or effective user.

## Key Interfaces

Flag groups include:
- caller-zone scopes: `VMUSAGE_SYSTEM`, `VMUSAGE_ZONE`, `VMUSAGE_PROJECTS`, `VMUSAGE_TASKS`, `VMUSAGE_RUSERS`, `VMUSAGE_EUSERS`.
- all-zone scopes: `VMUSAGE_ALL_ZONES`, `VMUSAGE_ALL_PROJECTS`, `VMUSAGE_ALL_TASKS`, `VMUSAGE_ALL_RUSERS`, `VMUSAGE_ALL_EUSERS`.
- collapsed-zone scopes: `VMUSAGE_COL_PROJECTS`, `VMUSAGE_COL_RUSERS`, `VMUSAGE_COL_EUSERS`.

`vmusage_t` reports zone ID, result type, entity ID, total/private/shared RSS, and total/private/shared swap reservation in bytes.

The user-facing function is:
- `getvmusage(uint_t flags, time_t age, vmusage_t *buf, size_t *nres)`

Kernel-side declarations include:
- `vm_getusage()`
- `vm_usage_init()`

## Research Notes

The comments define zone semantics carefully: non-global zones requesting all-zone or collapsed-zone data are reduced to local-zone scope. `VMUSAGE_SYSTEM` in a non-global zone returns a system-typed result, but only for the calling zone.
