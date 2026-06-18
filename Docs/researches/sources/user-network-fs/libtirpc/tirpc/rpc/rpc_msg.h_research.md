# sources/user-network-fs/libtirpc/tirpc/rpc/rpc_msg.h

Purpose: `rpc_msg.h` defines the ONC RPC message wire model for calls and replies plus XDR routines and error mapping.

Important APIs, types, and functions: It defines `RPC_MSG_VERSION`, `RPC_SERVICE_PORT`, enums `msg_type`, `reply_stat`, `accept_stat`, and `reject_stat`, structures `accepted_reply`, `rejected_reply`, `reply_body`, `call_body`, and `rpc_msg`, field aliases, and XDR functions `xdr_callmsg`, `xdr_callhdr`, `xdr_replymsg`, `xdr_accepted_reply`, `xdr_rejected_reply`, plus `_seterr_reply`.

Control flow: Clients encode `CALL` messages with program/version/procedure and auth credentials. Servers decode calls and encode `REPLY` messages as accepted or denied. Accepted replies may carry results, version mismatch ranges, or null bodies; denied replies carry RPC version mismatch or auth error data.

State and persistence behavior: No module state is declared. Message structs contain pointers to auth bodies and result XDR callbacks, so ownership remains with callers and auth/protocol layers.

Dependencies and integration points: It depends on `auth.h` and is used by every client/server transport, `svc_vc.c`, auth code, and error translation in `clnt.h`.

Risks: Union aliases make it easy to access the wrong arm if direction/status is not set first. `ar_results` embeds a function pointer and location for local XDR use, not a direct wire field. Version and status numeric values are protocol ABI.

Test signals: Tests should cover call header pre-serialization, accepted success results, all accepted/rejected error statuses, auth error mapping through `_seterr_reply`, and malformed message decode rejection.
