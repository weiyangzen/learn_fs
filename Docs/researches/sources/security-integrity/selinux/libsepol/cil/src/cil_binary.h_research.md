# sources/security-integrity/selinux/libsepol/cil/src/cil_binary.h

## Purpose
`cil_binary.h` declares the CIL-to-libsepol binary policy conversion interface. It exposes the top-level APIs for creating a `sepol_policydb_t` from a resolved `struct cil_db`, checking CIL neverallow rules against an existing `policydb_t`, and converting individual CIL declarations/rules/contexts into libsepol `policydb_t` structures.

The header is broader than a minimal public facade: it publishes many lower-level conversion helpers used by the implementation and nearby CIL code. Its declarations document the conversion surface between CIL AST data types and libsepol policydb data structures.

## Important APIs, Types, And Functions
The main lifecycle functions are `cil_binary_create(const struct cil_db *db, sepol_policydb_t **pdb)` and `cil_binary_create_allocated_pdb(const struct cil_db *db, sepol_policydb_t *pdb)`. The first allocates and initializes a policydb; the second fills an already allocated policydb for binary compatibility. `cil_check_neverallows_against_pdb` validates neverallow rules from a CIL db against a supplied policydb and returns a violation flag separately from fatal errors.

Declaration conversion functions include `cil_common_to_policydb`, `cil_class_to_policydb`, `cil_role_to_policydb`, `cil_type_to_policydb`, `cil_typealias_to_policydb`, `cil_typepermissive_to_policydb`, `cil_typeneveraudit_to_policydb`, `cil_typeattribute_to_policydb`, `cil_typeattribute_to_bitmap`, `cil_policycap_to_policydb`, `cil_user_to_policydb`, `cil_bool_to_policydb`, `cil_catorder_to_policydb`, `cil_catalias_to_policydb`, `cil_sensitivityorder_to_policydb`, and `cil_sepol_level_define`.

Relationship and rule conversion functions include `cil_roletype_to_policydb`, `cil_userrole_to_policydb`, `cil_type_rule_to_policydb`, `cil_avrule_to_policydb`, `cil_booleanif_to_policydb`, `cil_roletrans_to_policydb`, `cil_roleallow_to_policydb`, `cil_typetransition_to_policydb`, `cil_constrain_to_policydb`, and `cil_rangetransition_to_policydb`.

Context conversion functions include `cil_ibpkeycon_to_policydb`, `cil_ibendportcon_to_policydb`, `cil_portcon_to_policydb`, `cil_netifcon_to_policydb`, `cil_nodecon_to_policydb`, `cil_fsuse_to_policydb`, `cil_genfscon_to_policydb`, `cil_pirqcon_to_policydb`, `cil_iomemcon_to_policydb`, `cil_ioportcon_to_policydb`, and `cil_pcidevicecon_to_policydb`. `cil_level_to_mls_level` converts a CIL MLS level into libsepol `mls_level_t`.

The header includes `sepol/policydb/policydb.h` plus CIL internal/tree/list headers, so callers see libsepol policydb types and internal CIL structs in the same interface.

## Control Flow
The header itself has no runtime control flow, but its declarations reveal the intended conversion pipeline. Callers normally use `cil_binary_create`; compatibility callers may initialize a policydb themselves and call `cil_binary_create_allocated_pdb`. Fine-grained helpers are grouped by the order in which the implementation needs them: declarations first, role/user/type relationships next, access and transition rules, constraints and MLS ranges, then object contexts.

Several helper signatures require `const struct cil_db *db` in addition to a single CIL datum. Those functions need database-wide reverse maps or ordered value lists to expand attributes into concrete users, roles, types, classes, or MLS objects. Helpers that accept `struct cil_sort *` operate on already sorted context arrays, preserving deterministic binary output order.

## State And Persistence Behavior
Every conversion function declared here mutates the supplied `policydb_t` or `sepol_policydb_t`; none returns a detached converted object except via out parameters such as `common_datum_t **common_out`, `mls_level_t *mls_level`, or the top-level policydb pointer. Successful calls generally transfer allocated libsepol datums, bitmaps, avtab entries, constraints, or object contexts into the policy database.

The APIs return `SEPOL_OK` on success and an error code otherwise. `cil_check_neverallows_against_pdb` additionally writes `*violation` to distinguish a semantic neverallow violation from lower-level conversion/checking errors. Top-level creation owns allocation in `cil_binary_create`, while `cil_binary_create_allocated_pdb` assumes caller ownership of the policydb object.

## Dependencies And Integration Points
This header is the integration point between the CIL frontend and libsepol binary policy internals. It depends on CIL internal declarations from `cil_internal.h`, tree/list containers from `cil_tree.h` and `cil_list.h`, and libsepol policy database structures from `policydb.h`.

Most consumers should only need the top-level creation and neverallow-checking APIs. The lower-level declarations are useful for tests, compatibility, or adjacent translation code, but they expose internal sequencing assumptions: many functions require prior insertion of referenced users, roles, types, classes, permissions, categories, or sensitivities.

## Risks And Edge Cases
Because the header exposes many granular conversion functions, callers can invoke them out of order and receive lookup failures or partially populated policydb state. For example, rule insertion requires class/type/user/role symbols and value arrays to already exist, and MLS conversions require category and sensitivity order to have been inserted.

Some comments are stale or imprecise: several parameters are described as generic `datum` or `node` even when the signature takes a concrete CIL struct, and there is a typo in the typepermissive comment. The declaration `cil_class_to_policydb` appears in the header, but the implementation path uses class-order conversion rather than a matching exported function in this file, so consumers should verify linkage before relying on that symbol.

The API surface exposes internal CIL types and libsepol internals directly, which makes ABI/API stability sensitive to struct changes in either subsystem. Error handling is also coarse-grained: most functions return only `SEPOL_ERR`, so callers depend on logging for detailed diagnostics.

## Test Signals
Header-level tests are mostly compile/link and API contract tests. A smoke test should include this header from a C translation unit, call `cil_binary_create` and `cil_check_neverallows_against_pdb` through their declared prototypes, and verify the expected libsepol/CIL include dependencies are sufficient.

Integration tests should prefer the top-level creation API, then inspect the resulting policydb for inserted declarations, avtab entries, conditionals, MLS levels/ranges, and object contexts. Lower-level helper tests should explicitly build prerequisite policydb state first and should include out-of-order calls to confirm lookup failures are reported cleanly.
