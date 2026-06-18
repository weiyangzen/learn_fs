# sources/security-integrity/selinux/checkpolicy/module_compiler.h

## Purpose

`module_compiler.h` exposes the module compiler/scoping API used by the parser and semantic action layer. It is the contract for initializing policy/module scope, declaring and requiring symbols, checking whether references are allowed in the current module scope, appending parsed rule objects, and managing optional block lifetime.

## Important APIs and Types

The header includes `sepol/policydb/hashtab.h` because several APIs use `hashtab_key_t` and `hashtab_datum_t`. It relies on libsepol policydb types that are visible through the translation units including it, such as `role_datum_t`, `type_datum_t`, `user_datum_t`, `avrule_t`, `cond_list_t`, and transition rule structs.

`define_policy(int pass, int module_header_given)` begins parser handling for base or module input. `declare_symbol()` and `require_symbol()` are lower-level generic symbol insertion APIs. Typed wrappers (`declare_role()`, `declare_type()`, `declare_user()`, `require_class()`, `require_role()`, `require_type()`, `require_bool()`, and others) hide the datum setup and pass-sensitive behavior.

`is_id_in_scope()` and `is_perm_in_scope()` are semantic checks used before resolving names into policydb indexes. `get_current_cond_list()` deduplicates conditionals by expression within the active declaration. `append_cond_list()`, `append_avrule()`, `append_role_trans()`, `append_role_allow()`, `append_range_trans()`, and `append_filename_trans()` form the output side of parser reductions.

Optional blocks are controlled by `begin_optional()`, `begin_optional_else()`, `end_optional()`, and `end_avrule_block()`.

## Control Flow and Integration

`policy_parse.y` calls these APIs directly from grammar actions, while `policy_define.c` calls declaration, scope-check, local-symbol, and append functions while constructing policydb objects. The interface is pass-aware: many exported helpers receive `pass`, and callers are responsible for draining `id_queue` consistently even when pass 1 only declares skeletons and pass 2 resolves references.

## State and Persistence Behavior

The header does not define state, but all functions operate against global parser state declared in implementation files, especially `policydbp`, `id_queue`, and the module compiler scope stack. Objects appended through this API become part of the persistent `policydb_t` tree.

## Dependencies and Risks

Because this is a C header with no ownership annotations beyond comments, callers must obey return-code conventions. In particular `declare_symbol()` can return `1` to mean the symbol already existed and the caller must free the datum. Misinterpreting `require_symbol()` or `declare_symbol()` return values can leak or double-free datums and can corrupt scope bitmaps. The optional-block APIs must be balanced in grammar actions.

## Test Signals

Compile coverage should ensure all parser users see consistent prototypes. Behavioral tests should exercise each exported require/declaration wrapper, optional block transitions, and scope checks for symbols and permissions.
