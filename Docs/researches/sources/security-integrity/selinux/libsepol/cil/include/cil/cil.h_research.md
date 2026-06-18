# sources/security-integrity/selinux/libsepol/cil/include/cil/cil.h

## Purpose
`cil.h` is the public C API for libsepol's Common Intermediate Language compiler interface. It exposes an opaque `cil_db_t`, compilation entry points, policy/output serialization helpers, configuration setters, logging hooks, and memory-error hook registration.

## Important APIs, Types, and Functions
The header forward-declares `struct cil_db` and typedefs it as `cil_db_t`. Lifecycle and compilation functions are `cil_db_init`, `cil_db_destroy`, `cil_add_file`, `cil_compile`, and `cil_build_policydb`. Side-output functions are `cil_userprefixes_to_string`, `cil_selinuxusers_to_string`, `cil_filecons_to_string`, `cil_write_policy_conf`, `cil_write_parse_ast`, `cil_write_build_ast`, `cil_write_resolve_ast`, and `cil_write_post_ast`.

Configuration setters include `cil_set_disable_dontaudit`, `cil_set_multiple_decls`, `cil_set_qualified_names`, `cil_set_disable_neverallow`, `cil_set_preserve_tunables`, `cil_set_handle_unknown`, `cil_set_mls`, `cil_set_attrs_expand_generated`, `cil_set_attrs_expand_size`, `cil_set_target_platform`, and `cil_set_policy_version`. Neverallow checking against an external policydb is exposed through `cil_check_neverallows_against_pdb`.

Logging support includes `enum cil_log_level`, `cil_set_log_level`, `cil_set_log_handler`, and printf-annotated `cil_log`. `cil_set_malloc_error_handler` lets callers override allocation failure behavior.

## Control Flow
Clients allocate a database with `cil_db_init`, feed one or more CIL files with `cil_add_file`, call `cil_compile`, optionally build a binary `sepol_policydb_t` or serialized side files, then destroy the database with `cil_db_destroy`. AST write helpers represent different pipeline checkpoints and may run parts of the compile pipeline.

## State and Persistence Behavior
The database is opaque and heap-owned by the library. Setter calls mutate compiler behavior inside `cil_db_t`. String conversion helpers allocate output buffers returned through `char **out` and `size_t *size`; callers must free them according to library convention. `cil_build_policydb` returns a libsepol policy database pointer through `sepol_policydb_t **`.

## Dependencies and Integration Points
The header includes `<sepol/policydb/policydb.h>` for `sepol_policydb_t`/`policydb_t` and supports C++ consumers through `extern "C"`. It is implemented primarily by `cil/src/cil.c` and related compiler modules.

## Risks and Test Signals
Callers must respect pipeline ordering: adding files before compile, compiling before binary or policy output where required, and freeing allocated outputs. `cil_set_handle_unknown` is the only setter here that reports invalid input directly. Test signals include successful parse/compile/build-policy flows, correct side-output strings, logging handler invocation, and invalid handle-unknown rejection.
