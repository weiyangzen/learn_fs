# File Research: sources/os/bsd/netbsd-src/sys/sys/protosw.h

## Purpose
Defines the kernel networking protocol switch: protocol dispatch vectors, user request operations, control input/output commands, timer helpers, lookup functions, and wrappers for non-MPSAFE protocols.

## Main API
- Core structure: `struct protosw`.
- Protocol flags: `PR_ATOMIC`, `PR_ADDR`, `PR_CONNREQUIRED`, `PR_WANTRCVD`, `PR_RIGHTS`, `PR_LISTEN`, `PR_LASTHDR`, `PR_ABRTACPTDIS`, `PR_PURGEIF`, `PR_ADDR_OPT`.
- User request codes: `PRU_ATTACH` through `PRU_PURGEIF`, `PRU_NREQ`.
- Control commands: `PRC_*`, `PRC_NCMDS`, `PRC_IS_REDIRECT`.
- Control output commands: `PRCO_GETOPT`, `PRCO_SETOPT`.
- Kernel user request vector: `struct pr_usrreqs`.
- Timer globals/macros: `pfslowtimo_now`, `pffasttimo_now`, `PRT_SLOW_*`, `PRT_FAST_*`.
- Lookup/control dispatch: `pffindproto`, `pffindtype`, `pffinddomain`, `pfctlinput`, `pfctlinput2`.
- Wrappers: `PR_WRAP_USRREQS`, `PR_WRAP_CTLOUTPUT`, `PR_WRAP_CTLINPUT`, `PR_WRAP_INPUT`.

## Dependencies
Forward declares networking/socket structures. Kernel wrappers depend on `kernel_lock`, `softnet_lock`, and socket internals.

## Risks and Notes
The header preserves legacy protocol request IDs and optional request-name tables. Wrapper macros generate many static functions and should be used carefully to avoid name collisions. Non-MPSAFE wrappers serialize through global kernel or softnet locks.
