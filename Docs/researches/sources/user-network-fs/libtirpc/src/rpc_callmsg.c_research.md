<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_callmsg.c -->
# sources/user-network-fs/libtirpc/src/rpc_callmsg.c

Purpose: XDR serializer/deserializer for RPC call messages. It handles the call header plus credential and verifier opaque-auth fields.

Important APIs and functions: `xdr_callmsg(XDR *xdrs, struct rpc_msg *cmsg)` is the sole exported function. It supports optimized inline encode/decode paths and a generic fallback using `xdr_u_int32_t`, `xdr_enum`, and `xdr_opaque_auth`.

Control flow: encode validates `oa_length <= MAX_AUTH_BYTES`, attempts a single `XDR_INLINE` allocation for the fixed header plus rounded credential and verifier lengths, writes xid/direction/rpc version/program/version/procedure, and copies opaque bodies. Decode first tries to inline the fixed header, validates `CALL` direction and `RPC_MSG_VERSION`, allocates credential/verifier buffers with `mem_alloc` when `oa_base` is null, then reads opaque bodies either inline or via `xdr_opaque`. If optimized paths are unavailable, the generic XDR chain performs the same field ordering and validation.

State and persistence: the function can allocate `cb_cred.oa_base` and `cb_verf.oa_base` during decode; ownership follows the normal XDR/auth message lifecycle. It does not store global state.

Dependencies and integration points: used by server transports such as `svc_dg.c` and `svc_raw.c` to parse incoming calls, and by client transports elsewhere in libtirpc. It depends on IXDR macros, `MAX_AUTH_BYTES`, and the `struct rpc_msg` layout from public RPC headers.

Risks: callers must initialize `oa_base` to either null or valid writable buffers before decoding. Inline paths rely on correct rounded-length arithmetic. Overlong authentication data is rejected, but malformed streams may still leave partially allocated fields for the caller/XDR cleanup path to free.

Test signals: cover encode/decode round trips for AUTH_NONE, AUTH_SYS-sized credentials, maximum-size opaque auth, over-limit rejection, wrong direction/version rejection, preallocated versus null auth buffers, and fallback behavior with an XDR implementation where `XDR_INLINE` returns null.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_callmsg.c -->
