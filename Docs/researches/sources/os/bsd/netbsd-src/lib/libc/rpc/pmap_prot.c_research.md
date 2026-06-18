# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/pmap_prot.c

Read completely: 76 lines.

Implements `xdr_pmap()`, the XDR serializer for a v2 portmapper mapping: program, version, protocol, and port, all as unsigned long fields.

It is a minimal protocol helper used by pmap client calls and pmap list serialization. It validates non-null arguments with `_DIAGASSERT` and returns `FALSE` if any field fails to encode/decode.
