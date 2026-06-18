# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tiuser.h

## Purpose
User-level Transport Interface/TLI definitions for connection-oriented and connectionless transport programming.

## Main Interfaces
- Defines TLI event flags such as `T_LISTEN`, `T_CONNECT`, `T_DATA`, `T_EXDATA`, `T_DISCONNECT`, `T_UDERR`, and `T_ORDREL`.
- Defines send/receive flags `T_MORE` and `T_EXPEDITED`.
- Defines data structures `struct t_info`, `struct netbuf`, `struct netbuf32`, `struct t_bind`, `struct t_optmgmt`, `struct t_discon`, `struct t_call`, `struct t_unitdata`, and `struct t_uderr`.
- Defines allocation structure IDs `T_BIND`, `T_OPTMGMT`, `T_CALL`, `T_DIS`, `T_UNITDATA`, `T_UDERROR`, and `T_INFO`.
- Defines field masks `T_ADDR`, `T_OPT`, `T_UDATA`, `T_ALL`.
- Defines TLI states `T_UNINIT`, `T_UNBND`, `T_IDLE`, `T_OUTCON`, `T_INCON`, `T_DATAXFER`, `T_OUTREL`, `T_INREL`, and `T_BADSTATE`.
- Declares the classic TLI API: `t_open`, `t_bind`, `t_accept`, `t_connect`, `t_listen`, `t_rcv`, `t_snd`, `t_rcvudata`, `t_sndudata`, `t_optmgmt`, `t_sync`, `t_unbind`, `t_close`, and related routines.

## Dependencies And Relationships
Includes `sys/types.h` and `sys/tpicommon.h`. It is the public TLI consumer header layered over common TPI error, service type, and option definitions.

## Research Notes
This is a legacy networking API. The structures are used both for library allocations and syscall/ioctl mediation, so field layout compatibility matters.
