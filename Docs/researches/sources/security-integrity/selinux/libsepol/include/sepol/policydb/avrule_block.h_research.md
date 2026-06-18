# sources/security-integrity/selinux/libsepol/include/sepol/policydb/avrule_block.h

Purpose: Declares internal helpers for module AV rule blocks and declarations.

Important APIs and functions: `avrule_block_create/destroy/list_destroy`, `avrule_decl_create/destroy`, `get_avrule_decl`, `get_decl_cond_list`, `is_id_enabled`, and `is_perm_existent`.

Control flow: Parser/linker code creates blocks and declarations, attaches conditions/rules/symbol scopes, and later checks enabled declarations and permission existence.

State and persistence: Blocks own declaration lists, symbol tables, required/declared scope bitmaps, and module-name metadata. They are serialized indirectly as module policydb structures.

Dependencies and integration points: Includes internal `policydb.h`; implemented by `src/avrule_block.c`.

Risks: Scope bookkeeping controls whether optional/module declarations activate. Incorrect destruction leaks nested rule lists and bitmaps.

Test signals: Module parsing/linking with optional blocks, conditional declarations, and inherited common permissions validates these helpers.
