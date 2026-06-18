# File Research: sources/os/bsd/netbsd-src/sys/sys/idtype.h

Read completely: 62 lines.

## Purpose
Defines `idtype_t`, the ABI enum used by process-selection system calls.

## Main Interfaces
- `P_MYID`, `P_ALL`, `P_PID`, `P_LWPID`, `P_PPID`, `P_PGID`, `P_SID`, `P_CID`, `P_UID`, `P_GID`, `P_TASKID`, `P_PROJID`, `P_POOLID`, `P_ZONEID`, `P_CTID`, `P_CPUID`, `P_PSETID`.
- `_P_MAXIDTYPE` forces wide enum representation and leaves room for future values.

## Dependencies And Integration
Used by wait/signal/process-control APIs that select targets by identifier class.

## Risks And Edge Cases
- The header explicitly warns not to reorder or insert values in the middle because syscall ABI would break.
- Some Solaris-derived constants are not applicable to NetBSD but remain in the enum.

## Filesystem Relevance
Low. Process ABI support only indirectly affects filesystem operations.
