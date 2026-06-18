# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/t_kuser.h

## Purpose
Defines kernel TLI/TPI helper structures and function prototypes used by in-kernel transport clients.

## Main Interfaces
- `TIUSER`: kernel transport endpoint wrapper containing file pointer, transport provider info, and flags.
- `struct knetbuf`: STREAMS-backed kernel netbuf for received data.
- `struct t_kunitdata`: unitdata address/options/data container.
- Debug macro `KTLILOG()` under `KTLIDEBUG`.
- Flag `MADE_FP`.
- Kernel TLI operations:
  - `t_kalloc()`, `t_kfree()`
  - `t_kopen()`, `t_kclose()`
  - `t_kbind()`, `t_kunbind()`
  - `t_kconnect()`
  - `t_koptmgmt()`
  - `t_krcvudata()`, `t_ksndudata()`
  - `t_kspoll()`, `t_kgetstate()`
  - `tli_send()`, `tli_recv()`
  - `t_tlitosyserr()`, `get_ok_ack()`
- Size helper macros for TPI primitives.

## Dependencies And Relationships
Includes file, credential, STREAMS, and TLI user headers. Used by kernel subsystems that need transport-provider access through TLI/TPI rather than socket APIs.

## Research Notes
The comments note that `TIUSER` would need expansion for richer connection-oriented transport state. Current data structures are minimal wrappers around provider info and STREAMS messages.
