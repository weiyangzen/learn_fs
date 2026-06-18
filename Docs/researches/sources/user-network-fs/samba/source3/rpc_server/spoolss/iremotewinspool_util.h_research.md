# Research: sources/user-network-fs/samba/source3/rpc_server/spoolss/iremotewinspool_util.h

## Purpose

`iremotewinspool_util.h` declares the public opcode mapping helper for the IRemoteWinspool-to-spoolss bridge. It lets spoolss server code ask whether an incoming async winspool opcode has a corresponding spoolss proxy opcode.

## Important APIs, Types, and Functions

- `bool iremotewinspool_map_opcode(uint16_t opcode, uint16_t *proxy_opcode)`: returns whether `opcode` is supported and, on success, writes the mapped spoolss opcode through `proxy_opcode`.

## Control Flow and Integration

The header has no implementation logic. It is included by `iremotewinspool_util.c` and by dispatch/proxy code that needs the mapper. Consumers should call the function before attempting proxy dispatch and treat `false` as unsupported.

## State and Persistence Behavior

The header declares a stateless lookup API. There is no ownership transfer or allocation implied by the signature. The only output is the scalar `proxy_opcode`.

## Dependencies and Integration Points

The header relies on surrounding Samba includes for `bool` and `uint16_t`. Its single declaration integrates the IRemoteWinspool async interface with the existing spoolss RPC opcode namespace.

## Risks and Edge Cases

- There is no visible include guard in the file, so duplicate inclusion depends on build conventions or consumer include structure.
- The function contract does not specify behavior for a NULL `proxy_opcode`; consumers should not pass NULL.
- Because the header does not include generated opcode definitions, it remains lightweight but gives no compile-time linkage to the exact constants mapped by the implementation.

## Test Signals

Compile coverage should ensure the declaration is visible to all dispatch consumers. Functional coverage belongs with the implementation: known opcode success, unsupported opcode failure, and caller fallback behavior.
