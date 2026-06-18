# sources/user-network-fs/libtirpc/src/xdr.c

Purpose: `xdr.c` supplies generic External Data Representation filters for scalar integers, booleans, enums, opaque data, counted bytes, netobjs, discriminated unions, strings, and 64-bit integer families.

Important APIs, types, and functions: Public filters include `xdr_free`, `xdr_void`, `xdr_int`, `xdr_u_int`, `xdr_long`, `xdr_u_long`, fixed-width signed/unsigned 8/16/32/64-bit variants, `xdr_char`, `xdr_u_char`, `xdr_bool`, `xdr_enum`, `xdr_opaque`, `xdr_bytes`, `xdr_netobj`, `xdr_union`, `xdr_string`, `xdr_wrapstring`, `xdr_hyper`, and quad/longlong aliases. It uses `XDR_GETLONG`, `XDR_PUTLONG`, `XDR_GETBYTES`, and `XDR_PUTBYTES` from the active stream backend.

Control flow: Each filter switches on `xdrs->x_op`. Encode paths convert host values to XDR units through stream ops; decode paths read XDR units and assign host values; free paths are no-ops for scalars and release dynamic storage for counted bytes/strings. `xdr_opaque` pads to four-byte alignment. `xdr_bytes` and `xdr_string` first encode/decode lengths, enforce maximum sizes, allocate missing decode buffers, and clean up newly allocated storage on decode failure. `xdr_union` decodes the discriminant and dispatches the matching arm procedure or a default.

State and persistence behavior: The file itself has no long-lived state except the static zero-padding buffer and a static scratch buffer used by `xdr_opaque` to discard padding. Dynamic state is owned by caller-visible pointers passed into `xdr_bytes` and `xdr_string`, which may be allocated on decode and freed on `XDR_FREE`.

Dependencies and integration points: It depends on `rpc/xdr.h`, `rpc/types.h`, `rpc/rpc_com.h`, and stream-specific XDR backends such as memory, stdio, and record streams. Higher-level RPC message, auth, rpcbind, and generated protocol XDR routines build on these primitives.

Risks: Numeric conversions intentionally marshal C `long` through 32-bit XDR units, so platform width assumptions matter. Decode does not range-check downcasts from long to smaller integer types. `xdr_opaque` uses a static padding discard buffer, which is small and adequate for padding but not reentrant if misused outside the fixed padding path. `xdr_string` protects `size + 1` overflow, while `xdr_bytes` relies on caller-provided max sizes to bound allocation.

Test signals: Round-trip tests should cover all scalar widths, signed truncation edges, opaque padding lengths 0-3, max-size rejection, decode allocation/failure cleanup for strings and bytes, union default/missing-arm behavior, and `XDR_FREE` idempotence.
