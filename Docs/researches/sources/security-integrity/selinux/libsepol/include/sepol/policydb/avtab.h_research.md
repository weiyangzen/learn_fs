# sources/security-integrity/selinux/libsepol/include/sepol/policydb/avtab.h

Purpose: Defines the internal access-vector table used for TE allow/audit/type-transition and extended-permission rules.

Important APIs and types: `avtab_key_t`, `avtab_datum_t`, `avtab_extended_perms_t`, `avtab_node`, `avtab_t`; operations `avtab_init/alloc/insert/search/search_node/search_node_next/insert_nonunique/insert_with_parse_context/map/read/read_item/destroy/hash_eval`.

Control flow: Policy read/expand code allocates buckets, inserts sorted nodes keyed by source type, target type, class, and specified rule flavor, then decision code searches matching entries.

State and persistence: AVTAB nodes own optional xperm allocations and parse context pointers. Binary policy read/write serializes semantic entries but not parse context or merge flags.

Dependencies and integration points: Used by policydb, conditional rules, assertion checking, services, and expansion.

Risks: Uniqueness rules differ for normal and conditional tables. Extended permission masks and enabled bits require careful filtering.

Test signals: Duplicate detection, xperm read/write, conditional nonunique insertion, and access-decision searches validate this table.
