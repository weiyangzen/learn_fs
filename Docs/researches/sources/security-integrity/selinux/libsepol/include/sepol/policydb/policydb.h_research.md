# sources/security-integrity/selinux/libsepol/include/sepol/policydb/policydb.h

Purpose: Defines libsepol's internal policy database schema, binary policy versions, and lifecycle/manipulation entry points.

Important APIs and types: Major types include symbol datums, type/role sets, class/user/type/role datums, AV rules, role/range/filename transition rules, object contexts, genfs entries, scope indexes, AV rule blocks/declarations, and `policydb_t`. Exports init/destroy, image conversion, indexing, optimization, ISID loading, ocontext sorting, file transition insertion, assertion checks, symtab insertion, policy file I/O, and many datum lifecycle helpers.

Control flow: Policy readers populate symbol tables and object contexts, index value-to-name arrays, evaluate conditionals, expand/link modules, validate contexts, and write binary policy according to version/target flags.

State and persistence: `policydb_t` is the authoritative in-memory policy state: symbols, rules, conditionals, contexts, genfs, range/file transitions, caps, permissive/neveraudit maps, versions, and target platform.

Dependencies and integration points: Central dependency for all internal policydb modules and many public wrappers.

Risks: One-based symbol values, version-gated fields, target-specific ocontext meanings, and manual ownership make this high risk.

Test signals: Binary read/write across versions, module expansion, context validation, assertions, and fuzzing malformed policies validate it.
