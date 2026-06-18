# sources/security-integrity/selinux/libsepol/cil/src/cil.c

## Purpose
`cil.c` is a central implementation file for the CIL compiler core. It initializes global keyword strings, creates and destroys `cil_db`, runs the major parse/build/resolve/post/binary compile phases, serializes selected compiler outputs, maps AST/data flavors to destructors and symbol tables, and provides constructors for most CIL internal data structures.

## Important APIs, Types, and Functions
Public API implementations include `cil_db_init`, `cil_db_destroy`, `cil_add_file`, `cil_compile`, `cil_write_parse_ast`, `cil_write_build_ast`, `cil_write_resolve_ast`, `cil_write_post_ast`, `cil_build_policydb`, `cil_write_policy_conf`, `cil_userprefixes_to_string`, `cil_selinuxusers_to_string`, `cil_filecons_to_string`, and configuration setters such as `cil_set_disable_dontaudit`, `cil_set_disable_neverallow`, `cil_set_attrs_expand_generated`, `cil_set_attrs_expand_size`, `cil_set_preserve_tunables`, `cil_set_handle_unknown`, `cil_set_mls`, `cil_set_multiple_decls`, `cil_set_qualified_names`, `cil_set_target_platform`, and `cil_set_policy_version`.

Internal support includes `cil_init_keys`, `cil_root_init`, `cil_root_destroy`, `cil_destroy_data`, `cil_flavor_to_symtab_index`, `cil_node_to_string`, `cil_symtab_array_init`, `cil_symtab_array_destroy`, `cil_destroy_ast_symtabs`, `cil_get_symtab`, `cil_string_to_uint32`, `cil_string_to_uint64`, `cil_sort_init`, `cil_sort_destroy`, and many `cil_*_init` constructors for AST records including contexts, users, roles, types, classes, booleans, tunables, rules, file contexts, ports, nodes, genfs, hardware contexts, defaults, MLS, and source-info records.

## Control Flow
`cil_db_init` initializes the string pool, interns all CIL keyword tokens via `cil_init_keys`, creates parse and AST trees, initializes root data, sort buckets, side-output lists, special `self`, `notself`, and `other` type records, value lookup arrays, and default compiler options. `cil_add_file` copies caller data into a NUL-padded buffer, invokes `cil_parser`, and frees the temporary buffer.

`cil_compile` runs the standard pipeline: build AST from parse tree, destroy the parse tree, resolve the AST, qualify names, and post-process. The AST write helpers run subsets of the same pipeline and dump parse/build/resolve/post trees with `cil_write_ast`. `cil_build_policydb` delegates to `cil_binary_create`, while `cil_write_policy_conf` delegates to `cil_gen_policy`.

Destructor and mapping functions provide shared infrastructure for the tree/list layers: `cil_destroy_data` switches on `enum cil_flavor` and calls the correct typed destroy helper, `cil_flavor_to_symtab_index` maps declarative flavors to symbol-table slots, and `cil_get_symtab` walks from an AST node to the nearest appropriate root/block/macro/in/conditional symbol table. Constructor functions allocate and zero/default initialize record fields so later parser/build phases can fill strings, datum pointers, expressions, and values.

## State and Persistence Behavior
`cil_db` owns parse/AST trees, sort arrays for context outputs, ordering lists, side-output lists, declared strings, special type datums, and value lookup arrays. `cil_db_destroy` tears these down, destroys the string pool, frees value arrays, and nulls the caller's pointer. Side-output serialization functions allocate buffers for users/prefixes, seusers, and file contexts; they compute lengths first, allocate with `cil_malloc`, and write textual output into caller-returned buffers.

The file does not directly persist to disk except when callers pass `FILE *` to write functions. It mutates global interned-key pointers and the global CIL string pool during database initialization/destruction.

## Dependencies and Integration Points
Dependencies include libsepol policydb/symtab/ebitmap facilities and CIL modules for logging, memory, tree/list/symtab handling, parser, AST build, resolution, fully-qualified names, post-processing, binary generation, policy.conf generation, string pooling, and AST writing. This file is the hub between the public `cil.h` API and internal compiler phases.

## Risks and Edge Cases
The compile pipeline destroys `db->parse`, so parse-tree write operations must happen before full compile or on a fresh database. AST write helpers also consume/destroy parse state as they progress. Side-output functions assume resolved datum pointers and sorted lists are populated correctly before serialization. Many formatting helpers use `sprintf` after manual length calculation, so length bugs would become memory safety issues. The global string-pool lifecycle means multiple independent databases or unusual init/destroy ordering need scrutiny. A duplicated assignment of `CIL_KEY_CONDFALSE` appears in key initialization; it is harmless but suggests manual keyword lists are easy to desynchronize.

## Test Signals
Useful signals include CIL parser/compiler tests that cover successful compile, parse/build/resolve/post AST dumping, binary policy generation, policy.conf generation, MLS and non-MLS user/file-context serialization, invalid numeric parsing, invalid `handle_unknown` values, symbol table lookup from nested AST nodes, and leak/error-path testing across `cil_db_init`/`cil_db_destroy`.
