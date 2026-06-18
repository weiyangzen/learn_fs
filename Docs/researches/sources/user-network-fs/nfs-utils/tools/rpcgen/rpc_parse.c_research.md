<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.c

## Purpose

`rpc_parse.c` implements the hand-written parser for RPCL input, converting scanner tokens into `definition` AST nodes for constants, structs, unions, enums, typedefs, and RPC programs.

## Important APIs, Types, and Functions

`get_definition` is the parser entry point. `def_struct`, `def_union`, `def_enum`, `def_const`, `def_typedef`, and `def_program` parse each top-level construct. `get_declaration`, `get_prog_declaration`, `get_type`, and `unsigned_dec` parse type/declarator forms. `check_type_name` rejects names that would conflict with XDR helpers. Parsed nodes are appended to global `defined` through `isdefined`.

## Control Flow

The parser reads one top-level keyword, dispatches to the matching parser, consumes the trailing semicolon, records the definition, and returns it. Program parsing handles versions, procedures, result types, positional or optional argument names, newstyle multi-argument restrictions, generated argument struct names, procedure numbers, version numbers, and program numbers.

## State and Persistence Behavior

The parser allocates AST nodes and strings that live for the process and are stored in global `defined`. No on-disk state is changed directly; output modules later consume the AST.

## Dependencies and Integration Points

It depends on `rpc_scan.c` token APIs and `rpc_util.c` list/error helpers. It integrates with all output generators through the shared AST types in `rpc_parse.h`.

## Risks and Edge Cases

The parser uses manual allocation and little recovery; `error` exits. `def_const` accepts identifiers or string constants but not numeric token kinds beyond scanner representation as identifiers. Program arguments prohibit opaque and pointer-to-string forms, and arrays as procedure args require typedef except strings. Fixed buffers are used for generated argument names in `get_prog_declaration`.

## Test Signals

Parser tests should cover every grammar construct, invalid reserved names, void rules, multiple arguments with and without `-N`, arrays/vectors/pointers, unsigned numeric types, unions with default and continued cases, malformed punctuation, and generated argument names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.c -->
