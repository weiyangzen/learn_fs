# File Research: sources/os/bsd/netbsd-src/sys/sys/paravirt_membar.h

## Purpose
Declares a paravirtualized memory barrier synchronization hook.

## Main API
- `paravirt_membar_sync(void)`.

## Dependencies
None beyond the kernel build context.

## Risks and Notes
The header is intentionally minimal. Correctness depends on the platform implementation providing the required synchronization semantics.
