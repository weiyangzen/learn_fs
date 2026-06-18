<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_hout.c -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_hout.c

## Purpose

`rpc_hout.c` emits C header content for RPCL definitions: constants, structs, unions, enums, typedefs, program/version/procedure macros, client/server prototypes, argument structs, table declarations, free-result prototypes, and XDR prototypes.

## Important APIs, Types, and Functions

`print_datadef` emits non-program data definitions and records XDR declarations via `storexdrfuncdecl`. `print_funcdef` emits program declarations. `pstructdef`, `puniondef`, `penumdef`, `ptypedef`, and `pdeclaration` render C type syntax. `pprogramdef`, `pprocdef`, `pargdef`, and `parglist` render RPC program macros and prototypes. `print_xdr_func_def` emits ANSI or K&R XDR prototypes. `undefined2` controls whether to print struct/enum prefixes before types are defined.

## Control Flow

Header output first prints data definitions as the parser produces them, storing XDR function declarations. Then the main driver iterates the completed `defined` list to print program function declarations. Finally it prints all stored XDR declarations and optional dispatch table struct declarations.

## State and Persistence Behavior

The file appends `xdrfunc` nodes to global `xdrfunc_head`/`xdrfunc_tail` and writes to global `fout`. Generated headers persist type and function declarations for generated and user-written RPC code.

## Dependencies and Integration Points

It depends on parser AST definitions, type helpers from `rpc_util.c`, option flags (`newstyle`, `Cflag`, `CCflag`, `tblflag`, `mtflag`), and is coordinated by `rpc_main.c` header output.

## Risks and Edge Cases

Forward/prefix handling is order-sensitive. `storexdrfuncdecl` stores the name pointer directly rather than copying. Some generated prototypes support legacy K&R branches, increasing compatibility complexity. `define_printed` aborts if procedure ordering assumptions are violated internally.

## Test Signals

Generate headers for enums with implicit/explicit values, unions, typedef arrays/pointers/vectors, recursive-ish struct tags, multiple program versions, duplicate procedure names across versions, `-N`, `-M`, `-T`, `-k`, and C++ guard modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_hout.c -->
