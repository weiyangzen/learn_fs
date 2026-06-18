<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.h

## Purpose

`rpc_util.h` declares rpcgen's shared utility macros, global variables, option flags, internal lists, and cross-module generator entry points.

## Important APIs, Types, and Functions

It defines allocation and printing macros, `struct list`, `struct xdrfunc`, `PUT`/`GET`, scanner/IO globals, the global `defined` AST list, basic type and XDR function lists, option flags, parser utility declarations, and output entry points such as `emit`, `print_datadef`, `write_most`, `write_stubs`, and `write_tables`.

## Control Flow

There is no executable flow. Including modules use the declarations to share one process-wide compiler context.

## State and Persistence Behavior

The header exposes mutable globals rather than opaque contexts. This makes rpcgen a single-compilation-at-a-time process and couples scanner, parser, and emitters.

## Dependencies and Integration Points

It depends on `definition`, `bas_type`, and `relation` from `rpc_parse.h` and standard `FILE`. It is one of the central internal interfaces for all `rpc_*.c` files.

## Risks and Edge Cases

Global mutable state prevents reentrant or parallel use. Macros wrap raw `malloc` without consistent NULL checking. Some declarations duplicate `proto.h`, so signature drift is a maintenance risk.

## Test Signals

Compile all generator modules together under strict warnings; run multi-output generation to verify global state is reset correctly between passes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_util.h -->
