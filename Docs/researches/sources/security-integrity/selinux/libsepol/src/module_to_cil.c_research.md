# sources/security-integrity/selinux/libsepol/src/module_to_cil.c

## Purpose
Converts SELinux module/base policydb structures and module-package sidecar text blobs into CIL text. It is a formatter and semantic bridge: it walks policydb symbol tables, scopes, optional blocks, AV rules, role/range/file transitions, booleans/tunables, MLS data, object contexts, genfs contexts, policy capabilities, seusers, user_extra, and file_contexts, then emits CIL forms to a global `out_file`.

## Important APIs, Types, and Functions
Public entry points are `sepol_module_policydb_to_cil(FILE *, struct policydb *, int)`, `sepol_module_package_to_cil(FILE *, struct sepol_module_package *)`, and `sepol_ppfile_to_module_package(FILE *, struct sepol_module_package **)`. Internal helpers include output wrappers `cil_printf`/`cil_println`, scope helpers around `struct stack`, role/type alias gathering lists, type/role set conversion helpers, and many `*_to_cil` emitters. `func_to_cil[]` dispatches symbol kinds to class/role/type/user/boolean/sensitivity/category emitters.

## Control Flow
`sepol_module_policydb_to_cil()` validates base/module policy type, normalizes the module name, emits base-only defaults (`systemlow`, `object_r`, `cil_gen_require`, handleunknown, mls), builds role and typealias lookup lists, emits policycaps/object contexts/genfs contexts, and finally prints either unresolved module blocks (`blocks_to_cil`) or linked blocks (`linked_blocks_to_cil`). Block conversion pushes declarations on a scope stack, emits aliases and declared/required/additive symbols, then emits rules and generated attributes. Optional blocks are nested by comparing required-scope supersets; linked conversion chooses only enabled branches. `sepol_module_package_to_cil()` appends package sidecar conversions after policydb conversion.

## State and Persistence Behavior
State is transient except for output written to `FILE *out_file`. The converter mutates `pdb->name` for base policies or invalid CIL name characters, uses global caches `role_list` and `typealias_lists`, and cleans them at exit. It reads module-package buffers directly for seusers, netfilter contexts, user_extra, and file_contexts. It does not write binary policy, but it serializes a policydb/module-package view into CIL syntax.

## Dependencies and Integration Points
Depends on libsepol policydb data structures, hashtabs, ebitmaps, conditional policy, services permission string helpers, module package accessors, `kernel_to_common` SID helpers, tokenizer helpers from `private.h`, and system networking conversion functions. It integrates with the compiler/linker path that needs CIL output from `.pp` packages and with policydb version-specific structures already populated by the reader.

## Risks and Edge Cases
Output failures call `_exit(EXIT_FAILURE)`, which bypasses normal library cleanup. Unsupported constructs are dropped with warnings: fscon, netfilter_contexts, role dominance, and optional `else` branches. Non-trivial neverallow targets with `notself` are rejected. `search_attr_list()` appears to skip equal ebitmaps when `ebitmap_cmp(...) == 0`, which can prevent deduplication of generated attributes and inflate output. String parsing for package sidecars is strict and mutates token buffers. `fp_to_buffer()` doubles buffer size without an explicit overflow guard. Global `out_file` and global lists make the converter non-reentrant.

## Test Signals
Useful tests compare generated CIL for base, module, linked module, MLS/non-MLS, optional blocks, type aliases, xperms, genfs wildcard policycap, seusers/user_extra/file_contexts, and unsupported constructs. Regression tests should assert deterministic ordering for permission arrays, correct optional nesting, valid CIL for generated anonymous set attributes, proper cleanup on parse failures, and pipe/socket `.pp` input handling.
