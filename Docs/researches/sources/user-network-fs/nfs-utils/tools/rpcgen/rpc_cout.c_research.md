<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_cout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_cout.c

## Purpose

`rpc_cout.c` emits XDR encode/decode/free functions for data definitions and generated multi-argument program structs.

## Important APIs, Types, and Functions

`emit` dispatches definitions to `emit_union`, `emit_enum`, `emit_struct`, `emit_typedef`, or `emit_program`. `print_generic_header`, `print_header`, and `print_trailer` frame `bool_t xdr_*` functions. `print_ifstat` chooses `xdr_pointer`, `xdr_vector`, `xdr_array`, `xdr_bytes`, `xdr_string`, or direct `xdr_type` calls based on `relation`. `emit_struct`, `inline_struct`, `emit_inline`, and `emit_single_in_line` generate optional `XDR_INLINE` fast paths for basic types. `undefined` and `findtype` help print prefixed struct/enum sizes.

## Control Flow

For each parsed definition, constants are skipped, program definitions emit XDR routines only for newstyle multi-argument structs, and type definitions avoid self-alias duplicate routines. Each emitted function serializes each member or union arm, returning `FALSE` on the first failed XDR helper and `TRUE` at the end.

## State and Persistence Behavior

The generator writes to global `fout` and reads `defined`, `Cflag`, `inlineflag`, and the basic type list initialized by `c_initialize`. Generated code contains no persistence beyond marshaling caller-provided data.

## Dependencies and Integration Points

It relies on AST structures from `rpc_parse.h`, type helpers in `rpc_util.c`, and generated headers from `rpc_hout.c`. Output compiles against ONC/TIRPC XDR APIs and IXDR macros.

## Risks and Edge Cases

Manual string allocation and fixed buffers are common. Inline generation is complex and sensitive to basic type size metadata, vector lengths, and XDR operation modes. `print_ifstat` has separate object naming paths for arrays and vectors that can be fragile for unusual typedef chains. Generated code quality depends on valid parser restrictions.

## Test Signals

Generate and compile XDR code for structs with basic runs, arrays, vectors, strings, opaque data, pointers, unions with continued cases and defaults, typedef chains, self typedefs, and inline thresholds including `-i 0`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_cout.c -->
