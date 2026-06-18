# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tihdr.h

## Purpose
Defines TPI protocol primitive numbers, state values, primitive structures, kernel-only extended primitives, capability structures, option headers, and option alignment/traversal macros.

## Main Interfaces
- Primitive constants for connection, disconnection, data, expedited data, info, bind/unbind, unitdata, option management, orderly release, address, capability, and kernel extended primitives.
- State constants including TPI provider/user state machine values and `TS_NOSTATES`.
- Core TPI structures:
  - `T_conn_req`, `T_conn_res`, `T_discon_req`
  - `T_data_req`, `T_exdata_req`
  - `T_info_req`
  - `T_bind_req`, `T_unbind_req`
  - `T_unitdata_req`
  - `T_optmgmt_req`
  - `T_ordrel_req`
  - `T_addr_req`
  - corresponding indication/ack/error structures such as `T_conn_ind`, `T_conn_con`, `T_discon_ind`, `T_data_ind`, `T_exdata_ind`, `T_info_ack`, `T_bind_ack`, `T_error_ack`, `T_ok_ack`, `T_unitdata_ind`, `T_uderror_ind`, `T_optmgmt_ack`, `T_ordrel_ind`, and `T_addr_ack`
- Capability support:
  - `T_capability_req`
  - `T_capability_ack`
- Kernel extended structures:
  - `T_optdata_req`, `T_optdata_ind`, `T_extconn_ind`, and related extended primitive values.
- `struct T_opthdr`: TPI option header.
- Alignment and option iteration macros:
  - `__TPI_ALIGN()`, `__TPI_SIZE_ISALIGNED()`
  - primitive/option alignment helpers
  - `_TPI_TOPT_DATA()`, `_TPI_TOPT_DATALEN()`
  - `_TPI_TOPT_FIRSTHDR()`, `_TPI_TOPT_NEXTHDR()`, `_TPI_TOPT_VALID()`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/tpicommon.h`. Used by STREAMS TPI providers/consumers and kernel transport interfaces such as `t_kuser.h`.

## Research Notes
The header is version-sensitive through `_SUN_TPI_VERSION`, exposing old/new primitive names and capability support depending on the selected TPI version.
