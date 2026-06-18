# sources/security-integrity/selinux/libsepol/include/sepol/policydb/symtab.h

Purpose: Defines policy symbol tables backed by generic hash tables.

Important APIs and types: `symtab_datum_t` with one-based `value`, `symtab_t` with `hashtab_t table` and `nprim`, plus `symtab_init` and `symtab_destroy`.

Control flow: Policy readers/parsers insert named symbols with datum structs whose first field is `symtab_datum_t`; indexers build value-to-name arrays from `value`.

State and persistence: Symbol tables own name/datum mappings and primary-name counts within policydb or AV rule declarations.

Dependencies and integration points: Depends on `hashtab.h`; used for classes, roles, types, users, bools, levels, categories, permissions, scopes.

Risks: The "common first field" casting convention is easy to break. Zero is invalid for values; off-by-one indexing is common risk.

Test signals: Symbol insertion/indexing, duplicate names, destroy behavior, and value-to-name array population validate it.
