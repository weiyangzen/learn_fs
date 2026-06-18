# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/xdryp.c

## Purpose
Implements XDR serialization/deserialization routines for NetBSD’s YP/NIS protocol structures and exported Sun-compatible YP XDR API.

## Main Entry Points
Includes XDR functions for domain/map/owner strings, DBM `datum`, request structs (`ypreq_key`, `ypreq_nokey`, `ypreq_xfr`), bind responses, map parameters, push responses, value/key responses, master/order/maplist responses, maplist linked lists, IP addresses, and `xdr_ypall()` streaming callbacks.

## Control Flow
Most functions validate arguments with `_DIAGASSERT`, then serialize fields in protocol order using `xdr_string`, `xdr_bytes`, `xdr_opaque`, `xdr_enum`, `xdr_u_int`, and `xdr_pointer`. `xdr_ypall()` loops over streamed boolean “more” markers, decodes each key/value response into stack buffers, and invokes the caller callback until the server ends or callback asks to stop.

## Dependencies
Depends on RPC/XDR libc support, `rpcsvc/yp_prot.h`, `rpcsvc/ypclnt.h`, socket/IP structures, NetBSD weak aliases, and deprecated warning annotations for older buggy string routines.

## Risks And Notes
Some routines intentionally do not strictly match the RPC `.x` definition because they preserve historical Sun YP API behavior. `xdr_ypall()` uses fixed `YPMAXRECORD` stack buffers, so record-size limits are central to safety.
