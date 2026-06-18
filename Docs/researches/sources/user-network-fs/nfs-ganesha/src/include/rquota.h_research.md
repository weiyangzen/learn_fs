# sources/user-network-fs/nfs-ganesha/src/include/rquota.h

## Purpose
This hand-maintained rpcgen-style header defines the RQUOTA RPC protocol data model, client/server stubs, and XDR entry points.

## Important APIs, Types, And Control Flow
It defines quota block structures `sq_dqblk` and `rquota`, argument structures for regular and extended get/set quota calls, result unions `getquota_rslt` and `setquota_rslt`, `qr_status` values `Q_OK`, `Q_NOQUOTA`, and `Q_EPERM`, program/version constants `RQUOTAPROG`, `RQUOTAVERS`, and `EXT_RQUOTAVERS`, procedure numbers, client and `_svc` function prototypes, `rquotaprog_1_freeresult`, `check_handle_lead_slash`, and XDR functions for each protocol type.

## State And Persistence
The header defines RPC wire structures only. Runtime handlers read or mutate filesystem quota state via OS quota APIs; XDR functions serialize transient request/response objects.

## Dependencies And Integration Points
It depends on `gsh_rpc.h` and `extended_types.h`. It connects the RPC dispatch layer to rquota service implementations and the OS quota abstraction.

## Risks And Test Signals
Because this is protocol ABI, field order and integer widths are high-risk. Tests should include XDR encode/decode compatibility with rpcgen clients, procedure dispatch for v1 and extended v2 arguments, path length handling, leading-slash normalization, and quota status mapping.
