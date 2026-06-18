<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/proto.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/proto.h

## Purpose

`proto.h` centralizes cross-translation-unit prototypes for the bundled `rpcgen` implementation and supplies build-host compatibility shims when compiling for glibc build tooling.

## Important APIs, Types, and Functions

It declares output generator entry points (`write_stubs`, `emit`, `print_datadef`, `write_sample_svc`, `write_tables`, service helpers), parser/scanner utility functions (`get_definition`, `reinitialize`, `error`, `crash`, `tabify`, `make_argname`, `add_type`), and shared declaration printers such as `printarglist`, `pdeclaration`, and `pprocdef`.

## Control Flow

The header has no runtime flow; it permits the modular `rpc_*.c` files to call each other's generator helpers after including AST definitions.

## State and Persistence Behavior

It declares no storage directly, but exposes functions that operate on global parser/output state from `rpc_util.c` and option globals from `rpc_main.c`.

## Dependencies and Integration Points

It depends on types from `rpc_parse.h` and standard `FILE`. It is included late by generator files and contains an `IS_IN_build` block disabling gettext macros for cross-rpcgen builds.

## Risks and Edge Cases

Some prototypes overlap with `rpc_util.h`/`rpc_output.h`, and signatures differ in const-qualification in places, so compiler strictness matters. Because it is the common internal interface, mismatched declarations can affect multiple generator modes.

## Test Signals

Compile with strict warnings where possible, and exercise every output mode to ensure declared functions match definitions across C and K&R compatibility branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/proto.h -->
