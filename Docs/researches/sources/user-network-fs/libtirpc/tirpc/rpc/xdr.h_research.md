<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/xdr.h -->
# sources/user-network-fs/libtirpc/tirpc/rpc/xdr.h

## Purpose

This libtirpc public header defines the External Data Representation stream ABI used by ONC/RPC callers. It supplies the `XDR` handle, operation vector, primitive serializer prototypes, inline accessors, record/memory/stdio stream constructors, and network object helpers used by generated rpcgen code and hand-written RPC services. The source was read as a complete 378-line file (13372 bytes).

## Important APIs, Types, and Functions

types: `__rpc_xdr`, `xdr_ops`, `for`, `xdr_discrim`, `netobj`, `xdr_op` macros: `_TIRPC_XDR_H`, `BYTES_PER_XDR_UNIT`, `RNDUP`, `XDR_GETLONG`, `xdr_getlong`, `XDR_PUTLONG`, `xdr_putlong`, `XDR_GETINT32`, `XDR_PUTINT32`, `XDR_GETBYTES`, `xdr_getbytes`, `XDR_PUTBYTES`, and 34 more enum values: `xdr_op` (XDR_ENCODE, XDR_DECODE, XDR_FREE)

## Control Flow

Runtime flow is indirect through the `XDR` operation vector. Callers create a stream with memory/stdio/record constructors, serializers dispatch through `x_ops` to get/put bytes and positions, and higher-level XDR procedures compose primitive encoders based on `x_op` (`XDR_ENCODE`, `XDR_DECODE`, or `XDR_FREE`).

## State and Persistence Behavior

The header owns no persistent storage. State lives in caller-allocated RPC/XDR objects or generated service structures and is valid for the lifetime of the stream, request, response, or decoded allocation.

## Dependencies and Integration Points

direct includes: `stdio.h`, `netinet/in.h`, `rpc/types.h`

## Risks and Edge Cases

ABI compatibility is critical: changing `XDR`, `xdr_ops`, primitive prototypes, alignment macros, or inline integer conversion can break generated RPC code and wire compatibility. `XDR_CONTROL` macro shape also risks statement-context surprises.

## Test Signals

Compile consumers that include the header from C and C++; rpcgen/XDR round-trip tests for primitive and generated structures; ABI/layout checks where supported; interoperability tests against RPC clients/servers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/tirpc/rpc/xdr.h -->
