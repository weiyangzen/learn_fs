# sources/test-tools/strace/maint/gen/ast.h

Purpose: public AST type model for the decoder-definition generator.

Important APIs/types/functions: defines `ast_number`, `ast_node_type`, structs for syscalls, arguments, structs, flags, locations, type options, and `ast_type`. Standard type categories include `TYPE_BASIC`, `TYPE_CONST`, `TYPE_PTR`, `TYPE_REF`, `TYPE_XORFLAGS`, and `TYPE_ORFLAGS`; pointer direction helpers `IS_IN_PTR`, `IS_OUT_PTR`, and `IS_INOUT_PTR` support code generation.

Control flow: the header encodes the tree/list shape consumed by parser reductions, preprocessing, and code generation. AST nodes use a tagged union to represent statements such as syscalls, defines, includes, conditionals, flags, structs, and custom decoders.

State and persistence behavior: only type declarations and function prototypes; no storage except through users of these types.

Dependencies and integration points: included by almost every `maint/gen` C file. Its type contracts drive symbol resolution, variant grouping, decoder matching, and output generation.

Risks: changes are high blast radius across Bison actions and codegen. Flexible ownership of char pointers and nested type options is not obvious from the declarations, increasing leak/double-free risk for future modifications.

Test signals: full generator compile plus successful parse/codegen of existing `.def` files validates structural compatibility.
