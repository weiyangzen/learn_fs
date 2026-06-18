<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.h -->
# sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.h

## Purpose

`rpc_parse.h` defines the AST and core semantic enums used by the rpcgen scanner, parser, and output generators.

## Important APIs, Types, and Functions

It defines `defkind`, `relation`, `typedef_def`, `enumval_list`, `enum_def`, `declaration`, `decl_list`, `struct_def`, `case_list`, `union_def`, `arg_list`, `proc_list`, `version_list`, `program_def`, `definition`, and `bas_type`. It declares `definition *get_definition(void)`.

## Control Flow

The header has no executable flow. It establishes the in-memory schema that `rpc_parse.c` fills and output modules traverse.

## State and Persistence Behavior

AST objects are heap-allocated by the parser and stored in global lists declared in `rpc_util.h`. The structures represent source definitions only during a single rpcgen process.

## Dependencies and Integration Points

Every rpcgen C file depends on these types. `relation` drives output choices for alias, pointer, fixed vector, and variable array forms.

## Risks and Edge Cases

Many fields are raw `const char *` pointers to scanner-allocated strings or static token names, with no ownership model. Program argument declarations reuse struct declaration lists, so output code must honor `arg_num` and `newstyle` semantics.

## Test Signals

Compile coverage and parser/output integration tests should verify all AST variants are populated and consumed consistently, especially union defaults, multi-argument programs, and typedef relation chains.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/rpcgen/rpc_parse.h -->
