<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.h

## Purpose

`rpc_scan.h` defines rpcgen token kinds, token representation, and scanner API declarations.

## Important APIs, Types, and Functions

`enum tok_kind` enumerates identifiers, constants, punctuation, RPCL keywords, primitive types, program/version keywords, and EOF. `struct token` carries a kind and string pointer. The header declares scanner functions and noreturn expectation-error helpers.

## Control Flow

No executable flow exists. Parser code uses these declarations to consume and validate tokens.

## State and Persistence Behavior

No state is declared here. Scanner globals live in `rpc_util.c` and scanner-local statics live in `rpc_scan.c`.

## Dependencies and Integration Points

It is shared by `rpc_scan.c`, `rpc_parse.c`, and `rpc_util.c` for token names and expected-token diagnostics.

## Risks and Edge Cases

The token set reflects the supported RPCL grammar. Adding syntax requires coordinated updates to this enum, scanner keyword tables, parser logic, and diagnostic string tables.

## Test Signals

Compile tests and scanner/parser fixtures should verify each token kind is reachable and diagnostics render expected token names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_scan.h -->
