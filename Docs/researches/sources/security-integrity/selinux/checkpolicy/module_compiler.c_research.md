# sources/security-integrity/selinux/checkpolicy/module_compiler.c

## Purpose

`module_compiler.c` implements the module-aware scoping layer used by the `checkpolicy` yacc actions. It sits between grammar reductions in `policy_parse.y`/`policy_define.c` and libsepol's `policydb_t` data model. Its main job is to keep the current `avrule_block_t`/`avrule_decl_t` stack coherent, enforce where declarations and `require` statements are legal, create or require symbols in the correct scope, and append parsed rules to the active declaration.

The file is essential for binary policy modules and optional blocks. It distinguishes global/base parsing from module parsing, tracks optional and else branches, records required and declared scope bitmaps, and resolves inherited requirements in pass 2.

## Important APIs, Types, and Functions

The private `scope_stack_t` records stack frame type, active declaration, last appended AV rule, else-branch state, whether a require was seen, and parent frame. Stack type `1` is an avrule block; type `2` is reserved for conditionals but is only lightly used. Global parser state includes `stack_top`, `last_block`, and `next_decl_id`.

`define_policy(pass, module_header_given)` initializes the parse state after the grammar recognizes either a base policy or a module header. It validates `policydbp->policy_type`, consumes the module name/version from `id_queue` on pass 1, drains them on pass 2, resets the stack, pushes the global declaration, and resets declaration numbering.

`declare_symbol()` and `require_symbol()` are wrappers around `create_symbol()`. They call `symtab_insert()` with `SCOPE_DECL` or `SCOPE_REQ`, then set the matching bit in `decl->declared.scope` or `decl->required.scope`; `require_symbol()` also marks `stack_top->require_given`.

`declare_role()`, `declare_type()`, and `declare_user()` allocate libsepol datum objects, insert them via `declare_symbol()`, and maintain local per-declaration symbol tables (`p_roles`, `p_types`, `p_users`). `get_local_type()` and `get_local_role()` materialize local copies for symbols referenced in module declarations.

The `require_*()` family handles require-block grammar entries. `require_class()` is special because it also creates class permission symbols when allowed by module policy and records required class permission bitmaps via `add_perm_to_class()`.

`is_id_in_scope()` and `is_perm_in_scope()` provide semantic validation used by `policy_define.c`. They treat unknown identifiers as in-scope so callers can emit the more specific "unknown" error later.

`append_*()` functions attach parsed AV rules, conditionals, role transitions/allows, filename transitions, and range transitions to the active declaration. Optional block control is managed by `begin_optional()`, `begin_optional_else()`, `end_optional()`, and `end_avrule_block()`.

## Control Flow

Parsing starts with `define_policy()`, which sets up the global stack frame. Grammar actions then call declaration or require helpers while reductions consume names from `id_queue`. `is_creation_allowed()` prevents declarations and requirements inside conditionals and else branches. For optional blocks, pass 1 allocates new `avrule_block_t` and `avrule_decl_t` objects; pass 2 walks the previously built block chain and asserts declaration ids match `next_decl_id`.

At the end of a non-global avrule block, pass 1 enforces that non-else module/optional branches have a require section, except for base-policy nested cases. In pass 2, `end_avrule_block()` calls `copy_requirements()` so a child declaration inherits all parent required symbol and class-permission bitmaps.

## State and Persistence Behavior

All persistent state is in the global `policydbp` object and libsepol data structures attached to it. The file also has parse-session globals (`stack_top`, `last_block`, `next_decl_id`) that are reset by `define_policy()` and, for fuzz builds, `module_compiler_reset()`. It owns and frees queue strings in pass-specific paths and allocates policydb child structures whose lifetime is owned by policydb destroy routines.

## Dependencies and Integration Points

This file depends on libsepol policydb, avrule block, conditional, ebitmap, hashtab, and symtab APIs. It integrates with `policy_define.c` via exported declare/require/scope/append functions and with `policy_parse.y` through optional and require grammar actions. It consumes `id_queue` from `queue.c` and reports through scanner/parser `yyerror()` and `yyerror2()`.

## Risks and Edge Cases

The implementation is highly stateful. Queue consumption must match grammar order exactly, declaration ids must stay synchronized across both passes, and assertions in pass 2 assume pass 1 successfully built the same block topology. Memory ownership is subtle: several paths return `1` from symbol creation to signal that the caller must destroy an unused datum. Else branches intentionally disallow declarations and require blocks, and a missed `require_given` update will reject otherwise valid modules. The expression `dest_typdatum->flavor != isattr ? TYPE_ATTRIB : TYPE_TYPE` in local type/role checks is precedence-sensitive and should be reviewed carefully if touched.

## Test Signals

Useful tests include parsing base policies with no module header, modules with name/version headers, optional blocks with and without requires, optional else branches inheriting requirements, duplicate declarations, type/attribute and role/attribute flavor conflicts, class require permissions, and pass-2 reparse consistency. Fuzz builds can use `module_compiler_reset()` to verify clean reuse across parser invocations.
