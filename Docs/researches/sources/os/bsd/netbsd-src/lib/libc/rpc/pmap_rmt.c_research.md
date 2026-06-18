# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_rmt.c

Read completely: 177 lines.

Implements the legacy portmapper remote-call service. `pmap_rmtcall()` sends a UDP call to `PMAPPROC_CALLIT`, allowing lookup and invocation of a service procedure through the portmapper in one round trip.

`xdr_rmtcall_args()` is encode-only: it serializes program/version/procedure, reserves a length field, encodes caller-supplied arguments, computes the encoded length via XDR positions, then rewrites the length field. `xdr_rmtcallres()` is decode-only: it decodes the returned port and result length, then dispatches to the caller-supplied result XDR function.

This file is protocol glue for historical broadcast/remote-call flows; it assumes seekable XDR streams for the length rewrite.
