## sources/user-network-fs/libtirpc/src/pmap_prot.c

Purpose: Provides the XDR codec for the legacy `struct pmap` registration/query record.

Important APIs and control flow: `xdr_pmap(XDR *xdrs, struct pmap *regs)` asserts non-null inputs and serializes program, version, protocol, and port as unsigned longs in order. It returns `FALSE` at the first failed XDR primitive.

State and persistence: No local state. Decode/free behavior is entirely primitive scalar handling.

Dependencies and integration: Used by `pmap_getport`, pmap dump list XDR, and compatibility portmapper calls.

Risks and test signals: Legacy protocol uses `u_long`, so ABI width and XDR's fixed external representation matter. Tests should round-trip boundary values, malformed/truncated streams, and interoperate with `xdr_pmaplist`.
