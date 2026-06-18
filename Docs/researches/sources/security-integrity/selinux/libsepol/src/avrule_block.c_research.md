# sources/security-integrity/selinux/libsepol/src/avrule_block.c

Purpose: Implements lifecycle and lookup helpers for module AV rule blocks/declarations and scope checks.

Important APIs and functions: `avrule_block_create`, `avrule_decl_create`, `avrule_decl_destroy`, `avrule_block_destroy`, `avrule_block_list_destroy`, `get_decl_cond_list`, `is_id_enabled`, and `is_perm_existent`.

Control flow: Declaration creation allocates and initializes per-declaration symbol tables and scope bitmaps. Destroy paths recursively release conditionals, AV/range/role/filename rules, scopes, symtabs, and module name. Lookup helpers find equivalent conditional nodes, test enabled declarations through scope metadata, and search class/common permissions.

State and persistence: Manages heap-owned block/declaration structures embedded in `policydb_t.global` and module declaration indexes.

Dependencies and integration points: Uses policydb, conditional, avrule_block headers, ebitmap/symtab helpers, and linker/expander state.

Risks: Scope activation rules differ for roles/users versus other symbols. Destroy functions must match nested ownership exactly to avoid leaks or use-after-free.

Test signals: Optional/conditional module blocks, permission inheritance from commons, enabled declaration lookup, and leak checks validate behavior.
