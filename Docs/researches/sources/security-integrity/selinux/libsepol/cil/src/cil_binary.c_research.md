# sources/security-integrity/selinux/libsepol/cil/src/cil_binary.c

## Purpose
`cil_binary.c` is the main translator from a resolved CIL database (`struct cil_db`) into a libsepol binary `policydb_t`. It allocates and initializes the policy database, inserts CIL declarations and rules into libsepol symbol tables, avtabs, conditional structures, MLS ranges, object-context lists, default-labeling fields, and Xen/network context tables, then validates neverallow and bounds constraints before returning a usable binary policy database.

The file also exposes helper entry points for checking CIL neverallow rules against an existing `policydb_t`. Its role is not parsing CIL text; it assumes the AST, symbol tables, class order, category/sensitivity order, attributes, and sorted context lists have already been built elsewhere in the CIL pipeline.

## Important APIs, Types, And Functions
Top-level public functions are `cil_binary_create`, `cil_binary_create_allocated_pdb`, and `cil_check_neverallows_against_pdb`. `cil_binary_create` allocates a `sepol_policydb_t`, initializes kernel policy metadata from `struct cil_db`, delegates to `cil_binary_create_allocated_pdb`, and frees the policydb on failure. `cil_binary_create_allocated_pdb` is the compatibility path for callers that already allocated and initialized the policydb.

The implementation uses `struct cil_args_binary` to carry the CIL db, target policydb, pass number, neverallow list, role-transition duplicate-detection table, extended-permission aggregation tables, and CIL type reverse map through tree walks. `struct cil_args_booleanif` carries conditional conversion state for `booleanif` true/false blocks. `struct cil_args_xperm_tables` groups separate ioctl and nlmsg extended-permission hashtabs.

Symbol/declaration conversion APIs include `cil_common_to_policydb`, `cil_role_to_policydb`, `cil_type_to_policydb`, `cil_typeattribute_to_policydb`, `cil_user_to_policydb`, `cil_bool_to_policydb`, `cil_policycap_to_policydb`, `cil_catorder_to_policydb`, `cil_catalias_to_policydb`, `cil_sensitivityorder_to_policydb`, and the private class-order conversion helper. These populate libsepol symbol tables and reverse value arrays.

Relationship and rule conversion APIs include `cil_roletype_to_policydb`, `cil_userrole_to_policydb`, `cil_type_rule_to_policydb`, `cil_typetransition_to_policydb`, `cil_avrule_to_policydb`, `cil_roletrans_to_policydb`, `cil_roleallow_to_policydb`, `cil_booleanif_to_policydb`, `cil_constrain_to_policydb`, the private `cil_validatetrans_to_policydb`, `cil_rangetransition_to_policydb`, and the default-labeling helpers. These expand CIL attributes and classpermission maps into concrete sepol values and attach them to avtabs, conditional avtabs, role transition lists, class constraints, and range-transition hashtabs.

Context and MLS APIs include `cil_level_to_mls_level`, `cil_sepol_level_define`, `cil_sidorder_to_policydb`, and object-context converters for `ibpkeycon`, `portcon`, `netifcon`, `ibendportcon`, `nodecon`, `fsuse`, `genfscon`, Xen `pirqcon`, `iomemcon`, `ioportcon`, `pcidevicecon`, and private `devicetreecon`. Shared helpers translate CIL contexts into `context_struct_t` and CIL level ranges into `mls_range_t`.

Validation helpers include `cil_check_neverallows`, `cil_check_neverallow`, `cil_check_type_bounds`, `cil_avrule_from_sepol`, and reporting helpers that find matching AST allow rules and print source context. The file relies on libsepol `check_assertion`, `bounds_check_users`, `bounds_check_roles`, and `bounds_check_type`.

## Control Flow
Binary creation follows a strict multi-stage pipeline. `cil_binary_create` calls `__cil_policydb_create`, which allocates a sepol policydb and sets `POLICY_KERN`, target platform, policy version, unknown handling, and MLS mode. `cil_binary_create_allocated_pdb` then allocates reverse maps for types/classes/perms, initializes classes and MLS ordering with `__cil_policydb_init`, allocates normal and conditional avtabs, creates duplicate-detection/aggregation hashtabs, and initializes the neverallow collection list.

The main AST conversion uses three full tree-walk passes through `__cil_binary_create_helper` and `__cil_node_to_policydb`. Abstract blocks and macros are skipped; `booleanif` children are skipped during ordinary walking because `cil_booleanif_to_policydb` handles their internal true/false blocks explicitly.

Pass 1 inserts primary declarations: roles, types, kept type attributes, policy capabilities, users, booleans, category aliases when MLS is enabled, and sensitivity definitions when MLS is enabled. After pass 1, `__cil_policydb_val_arrays_create` builds libsepol value-to-name and value-to-struct arrays, which later conversion logic needs for logging, class lookups, conditional evaluation, and bounds reporting.

Pass 2 inserts second-order relationships and rules that require the declarations to exist: type/user/role bounds, type aliases, permissive and neveraudit type bitmaps, type-attribute bitmaps, sensitivity aliases, role-to-type maps, user levels/ranges/roles, type rules, named type transitions, role transitions, constraints, validate transitions, range transitions, and class default-labeling settings. Neverallow and neverallowx AST nodes are collected rather than inserted into the policy avtab.

Pass 3 inserts booleans and allow-like rules: `booleanif` nodes become libsepol conditional nodes and conditional avtab entries; normal `allow`, `auditallow`, `dontaudit`, and extended-permission rules are inserted or aggregated; roleallow rules are linked. Extended permissions are first unioned in per-kind hashtabs keyed by avtab key, then flushed to `te_avtab` or `te_cond_avtab`.

After the passes, `cil_sidorder_to_policydb` preserves initial SID numbering and contexts, and `__cil_contexts_to_policydb` appends all sorted object contexts. If no kept type attributes initialized the type/attribute bitmaps, `__cil_typeattr_bitmap_init` creates identity maps. Conditional lists are optimized and enabled flags are set from current boolean values. Unless disabled, neverallows and user/role/type bounds are checked; violations turn creation into `SEPOL_ERR`. Finally, role and user caches are expanded for context validation, and an empty TE avtab is rejected.

## State And Persistence Behavior
The file mutates an in-memory libsepol `policydb_t`; it does not serialize the binary policy to disk. Persistence in this context means ownership transfer into policydb structures: inserted symbol-table keys, datum objects, avtab entries, linked `ocontext_t` lists, genfs lists, role-transition nodes, range-transition hashtable entries, conditional nodes, class constraints, and bitmaps remain attached to the policydb after success.

Temporary state is carefully bounded to the conversion call: reverse CIL maps, role transition hashtable, xperm aggregation hashtabs, class/permission reverse maps, and the neverallow list are freed in `cil_binary_create_allocated_pdb` exit handling. `cil_binary_create` owns the allocated sepol wrapper on failure and frees it. The compatibility entry point takes a caller-owned policydb; if it fails after partial mutation, cleanup of partially inserted policydb contents is left to the caller's normal policydb destruction path.

The translator relies heavily on libsepol numeric values starting at 1. Temporary reverse arrays allocate one extra slot and use sepol values directly for CIL reverse lookups. Policydb arrays use zero-based `value - 1` indexing.

## Dependencies And Integration Points
This file integrates with libsepol internals through `policydb.h`, `polcaps.h`, `conditional.h`, `constraint.h`, `expand.h`, and `hierarchy.h`. It uses libsepol symbol tables, avtabs, conditional nodes, ebitmaps, object contexts, MLS helpers, policy capability mapping, assertion checks, and bounds checks.

It depends on CIL internal modules for AST shape and memory helpers: `cil_internal.h`, `cil_flavor.h`, `cil_log.h`, `cil_mem.h`, `cil_tree.h`, `cil_binary.h`, `cil_symtab.h`, `cil_find.h`, and `cil_build_ast.h`. It assumes earlier CIL phases have populated `db->classorder`, `db->catorder`, `db->sensitivityorder`, `db->val_to_type`, `db->val_to_role`, `db->val_to_user`, type/user/role attribute bitmaps, sorted object-context arrays, and `cil_avrule` source strings used in diagnostics.

Key external integration points are `cil_binary_create` for normal compilation, `cil_binary_create_allocated_pdb` for older callers that preallocate policydbs, and `cil_check_neverallows_against_pdb` for validating neverallow rules against an externally supplied policydb. The neverallow and bounds diagnostics integrate back with the CIL AST by calling `cil_find_matching_avrule_in_ast` and printing parent source paths.

## Risks And Edge Cases
The conversion order is fragile: later passes assume declarations and value arrays are complete. Moving conversion steps across passes can break reverse lookups, conditional evaluation, or diagnostics.

Attribute expansion can be expensive. `self`, `notself`, `other`, expanded source attributes, expanded target attributes, role attributes, user attributes, classpermission maps, and extended permissions all multiply into concrete sepol entries or bitmaps. Large attributes or low `attrs_expand_size` thresholds can create significant CPU and memory load.

Extended permission handling has several special cases: ioctl full-driver ranges are represented differently from partial function ranges, nlmsg and ioctl are stored in separate aggregation tables, and conditional extended permissions require policy version `POLICYDB_VERSION_COND_XPERMS`. Incorrect aggregation could silently merge or split rule semantics.

Duplicate and conflict handling varies by rule kind. Ordinary allow-like rules merge permission bits, dontaudit intersects negated data, type rules reject conflicting results, named type transitions tolerate identical duplicates but reject conflicts, role transitions use a custom hashtable, and range transitions compare MLS ranges. Tests need to cover both duplicate-identical and duplicate-conflicting cases.

Memory ownership is subtle. Many allocations are transferred into libsepol tables and linked lists, while temporary xperm objects, neverallow avrules, class-perm nodes, and reverse maps are local. Error paths depend on whether insertion succeeded. A few helper exit paths are risky because they call datum destroy/free on pointers obtained from policydb lookups in failure cases, notably the permissive and neveraudit type helpers if bitmap mutation fails.

Context conversion is platform- and policy-version-sensitive. MLS-only constructs are skipped when MLS is disabled. Xen object contexts are only emitted for `SEPOL_TARGET_XEN`. `genfscon` path handling changes when `POLICYDB_CAP_GENFS_SECLABEL_WILDCARD` is set by appending `*` to stored paths. Conditional extended permissions are rejected for older policy versions.

`cil_check_neverallow` builds temporary sepol `avrule_t` assertions from CIL nodes and then runs libsepol assertion checking. If reverse class/permission mappings are incomplete, diagnostics can fail while trying to report a violation. Bounds reporting similarly converts bad sepol avtab entries back to CIL rules, so correctness depends on the temporary value-to-CIL maps allocated during binary creation.

## Test Signals
Useful positive tests compile policies containing classes/common permissions, roles, users, booleans, types, aliases, kept and unkept attributes, policy capabilities, MLS sensitivities/categories, object contexts, conditional allow rules, extended ioctl/nlmsg rules, type transitions with and without file names, role transitions, constraints, validate transitions, range transitions, and default-labeling statements.

Negative tests should assert failures for conflicting type transitions, conflicting named type transitions, conflicting role/range transitions, invalid conditional statements, named type transitions inside booleanifs, conditional xperms below the required policy version, neverallow violations, user/role/type bounds violations, missing SID order behavior, invalid context references, invalid network protocol mappings, and policies with no avrules.

Regression tests should verify the three-pass ordering by checking that value arrays, type-attribute bitmaps, conditional enabled flags, role/user caches, and object contexts are populated after success. Extended-permission tests should cover contiguous ranges, complete ioctl drivers, partial ioctl functions, nlmsg permissions, duplicate unioning, and dontaudit suppression through `db->disable_dontaudit`. Diagnostics tests should run with normal and verbose log levels to cover truncation of reported matching allow rules.
