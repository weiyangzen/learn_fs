# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vmsystm.h

## Role

`vmsystm.h` exposes miscellaneous VM subsystem globals, tunables, constants, and helper prototypes used inside the kernel.

## Key Interfaces

It declares page-accounting globals such as `freemem`, `avefree`, `avefree30`, `deficit`, `nscan`, `desscan`, `slowscan`, `fastscan`, `pushes`, `low_mem_scan`, and `n_throttle`.

Writable tunables include `maxpgio`, `lotsfree`, `desfree`, `minfree`, `needfree`, `throttlefree`, `pageout_reserve`, and `pages_before_pager`.

`NOMEMWAIT()` detects contexts that must not sleep while freeing memory: pageout, fsflush, scheduler, or `T_PUSHPAGE` threads.

The header also defines swapout flags, user-range validation return codes, large-page mapping flags, VAC alignment flags, and prototypes for address selection, user access checks, page-size selection, mapping helpers, VM metering, copy-on-write mapin, physical-page temporary mapping, memory PFN checks, cache flushing, boot virtual allocation, and exec stack-page slewing.

## Research Notes

This is an internal VM coordination header. Many declarations are architecture- or subsystem-sensitive, and several globals are core memory-pressure control inputs.
