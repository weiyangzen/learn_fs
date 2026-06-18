# File Research: sources/os/bsd/netbsd-src/sys/sys/pserialize.h

## Purpose
Declares passive serialization primitives for reader sections and writer grace-period synchronization.

## Main API
- Opaque type: `pserialize_t`.
- Functions: `pserialize_init`, `pserialize_create`, `pserialize_destroy`, `pserialize_perform`, `pserialize_read_enter`, `pserialize_read_exit`, `pserialize_in_read_section`, `pserialize_not_in_read_section`.

## Dependencies
Kernel-only.

## Risks and Notes
Readers use enter/exit tokens; writers use `pserialize_perform` to wait for pre-existing readers to drain. Objects removed from pserialize-protected structures must not be freed before the grace period.
