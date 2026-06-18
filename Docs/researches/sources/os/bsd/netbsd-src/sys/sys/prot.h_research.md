# File Research: sources/os/bsd/netbsd-src/sys/sys/prot.h

## Purpose
Declares common credential-change helpers and flag masks for `setresuid`/`setresgid` semantics.

## Main API
- Permission relation flags: `ID_E_EQ_E`, `ID_E_EQ_R`, `ID_E_EQ_S`, `ID_R_EQ_E`, `ID_R_EQ_R`, `ID_R_EQ_S`, `ID_S_EQ_E`, `ID_S_EQ_R`, `ID_S_EQ_S`.
- Functions: `do_setresuid`, `do_setresgid`.

## Dependencies
Uses `struct lwp`, `uid_t`, `gid_t`, and `u_int` from surrounding kernel/system includes.

## Risks and Notes
The flags describe which current IDs may authorize setting which target IDs. Callers must pass the right policy mask for the specific syscall variant.
