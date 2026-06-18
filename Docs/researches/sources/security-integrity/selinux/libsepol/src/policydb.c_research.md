# sources/security-integrity/selinux/libsepol/src/policydb.c

## Purpose
Core implementation of SELinux/Xen policy database lifecycle, indexing, binary reading, compatibility handling, symbol/scoping management, and destruction. It is the central deserializer and in-memory contract for libsepol policydb users.

## Important APIs, Types, and Functions
Key exported functions include `policydb_lookup_compat`, datum init/destroy helpers, `policydb_init`, `symtab_insert`, `type_set_cpy`, `type_set_or_eq`, `policydb_index_classes`, `policydb_index_bools`, `policydb_index_others`, `policydb_destroy`, `symtabs_destroy`, `scope_destroy`, `policydb_load_isids`, `avrule_read_list`, `policydb_read`, `policydb_reindex_users`, `policy_file_init`, `policydb_set_target_platform`, and `policydb_sort_ocontexts`. Static reader functions cover every serialized component: symbols, constraints, MLS levels/ranges, AV rules, filename/range/role transitions, ocontexts, genfs, scopes, and module blocks.

## Control Flow
`policydb_init()` creates symbol and scope tables, an initial global avrule block/declaration, object_r, AV tables, conditional policy state, filename/range transition hash tables, and ebitmaps. `policydb_read()` validates magic/string/version/config/table sizes, resolves compatibility info, reads optional module name/version and policy capability maps, reads symbol tables, indexes classes and other symbols, reads kernel AV/conditional/transition tables or module avrule blocks and scopes, reads ocontexts/genfs/range transitions, builds kernel type/attribute maps, and finally validates the policy. Destruction mirrors allocation through symbol destroy callbacks and specialized ocontext/genfs/transition cleanup.

## State and Persistence Behavior
This file owns the binary policy persistence format reader. Endianness is normalized with `le32_to_cpu`/`le64_to_cpu`, and many reads are version-gated by kernel/base/module policy version and target platform. In-memory persistent state includes hashtabs, ebitmaps, val-to-name/struct indexes, scope metadata, ocontext/genfs lists, transition tables, AV tables, role/user caches, and type/attribute maps. On read failure it returns `POLICYDB_ERROR`; callers are responsible for final cleanup unless specific helper paths clean partial objects.

## Dependencies and Integration Points
Integrates with policydb public wrappers, binary writer functions, conditional policy code, avtab, ebitmap, MLS helpers, expand/cache logic, policy validation, kernel/common target definitions, debug logging, and module/CIL conversion. `policydb_compat[]` is the compatibility matrix for serialized layout across policy versions and target platforms.

## Risks and Edge Cases
The reader is large and failure cleanup is uneven: many nested read errors return immediately after partial allocation, relying on later `policydb_destroy()` by callers. `symtab_insert()` comments that post-insert failures can leave inconsistent state. Version gates are numerous, so adding a policy feature requires coordinated updates to compatibility, read/write, validation, CIL conversion, and public bounds. Filename transition compact format validation prevents duplicate otypes or overlapping stypes, while compat mode intentionally ignores old duplicate rules. Scope reads reject symbols absent from symbol tables and zero/saturated decl lists. Kernel type_attr_map construction rejects attributes associated with attributes.

## Test Signals
High-value tests include binary policy corpus read/validate across min/max kernel and module versions, malformed length/count/bitmap fuzzing, duplicate symbol/scope/genfs/filename transition rejection, MLS and non-MLS context reads, SELinux versus Xen ocontext reads, role/user cache expansion, type/attribute map construction, round-trip read/write validation, and leak/error-path tests under allocation failure.
