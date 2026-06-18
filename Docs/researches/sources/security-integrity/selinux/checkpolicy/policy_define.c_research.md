# sources/security-integrity/selinux/checkpolicy/policy_define.c

## Purpose

`policy_define.c` is the semantic action engine for the SELinux checkpolicy grammar. It consumes identifier segments accumulated in `id_queue` by `policy_parse.y`, validates them against current scope and policy mode, creates libsepol policydb objects, and appends rules, contexts, constraints, booleans, MLS structures, and module declarations. It is the largest bridge between textual policy syntax and the in-memory `policydb_t`.

## Important APIs, Types, and Functions

Global parser state includes `policydb_t *policydbp`, `queue_t id_queue`, `unsigned int pass`, and `int mlspol`. `init_parser()` resets line counters, errors, pass number, source file, and the identifier queue. `insert_id()` and `insert_separator()` are called by grammar productions to enqueue strings and NULL separators.

Symbol and declaration actions include `define_class()`, `define_common_perms()`, `define_av_perms()`, `define_polcap()`, `define_bool_tunable()`, `define_attrib()`, `define_type()`, `define_typealias()`, `define_typeattribute()`, `define_typebounds()`, `define_role_types()`, `define_role_attr()`, `define_roleattribute()`, `define_attrib_role()`, and `define_user()`.

Rule actions include `define_te_avtab()`, `define_te_avtab_extended_perms()`, `define_compute_type()`, `define_filename_trans()`, `define_role_trans()`, `define_role_allow()`, `define_range_trans()`, and their conditional variants. Helpers such as `set_types()`, `set_roles()`, `read_classes()`, and extended-permission range builders translate grammar sets into bitmaps and rule nodes.

MLS and constraint actions include `define_sens()`, `define_dominance()`, `define_category()`, `define_level()`, `define_constraint()`, `define_validatetrans()`, `define_cexpr()`, and semantic category parsing helpers.

Object context actions include `define_initial_sid_context()`, Xen-specific `define_pirq_context()`, `define_iomem_context()`, `define_ioport_context()`, `define_pcidevice_context()`, `define_devicetree_context()`, SELinux network/context functions (`define_port_context()`, `define_netif_context()`, IPv4/IPv6 node variants), Infiniband functions, `define_fs_use()`, and `define_genfs_context()`.

## Control Flow

The file is designed around two parser passes. Pass 1 generally declares symbols, builds optional/module skeletons, and drains queue entries for constructs that cannot be fully resolved yet. Pass 2 validates references, expands sets, appends real rules, and fills contexts. Many functions start with a `pass` branch that consumes queued identifiers and returns early.

For TE rules, the grammar queues source types, target types, classes, and permissions separated by NULLs. `define_te_avtab_helper()` builds an `avrule_t`, handles `self`/`-self`, wildcard and complement permission syntax, validates permission scope, and returns a rule appended by `append_avrule()`. Extended permissions add a template rule, parse ioctl or netlink ranges, normalize omitted ranges, split complete/partial drivers, and append one or more `avrule_t` nodes with `av_extended_perms_t`.

For object contexts, functions parse raw numeric or address arguments from grammar semantic values plus queued strings, call `parse_security_context()`, validate platform support, check duplicates/overlap/hiding, and insert into `policydbp->ocontexts` or `policydbp->genfs`.

## State and Persistence Behavior

All successful definitions mutate `policydbp`. Common persistent structures include symbol tables, value-to-name indexes, role/type/user local declarations, `avrule_decl_t` lists, conditional lists, role transition lists, filename transition tables, MLS semantic ranges, `ocontext_t` linked lists, and genfs linked lists. Temporary queue strings are usually freed as they are consumed. Rule and context nodes become owned by policydb destruction once appended.

## Dependencies and Integration Points

This file depends on libsepol policydb, services, conditional, hierarchy, expand, polcaps, and module-compiler APIs. It receives syntax shape from `policy_parse.y`, tokens and source locations from `policy_scan.l`, and queue operations from `queue.c`. The append and scope functions in `module_compiler.c` are critical for module correctness.

## Risks and Edge Cases

The dominant risk is queue discipline: every grammar production must enqueue exactly what the target define function expects. A mismatch can silently shift later fields. Many functions must drain queues on pass 1 to keep pass 2 clean. The file is not reentrant because of global parser state. Memory ownership varies between "free immediately", "insert into policydb", and "destroy on error"; changes need careful error-path review.

Semantic edge cases include policy-version gating for conditional extended permissions, target-platform gating for Xen versus SELinux object contexts, duplicate and overlap checks for ports/nodes/ibpkeys, class permission vector width limits, forbidden dot syntax for MLS identifiers and aliases, `self` handling with complements, and prohibition on mixing booleans and tunables in one conditional expression.

## Test Signals

High-value tests parse policies covering class/common permission declarations, default rules, MLS definitions, type aliases/attributes/bounds, AV rules with `*`, `~`, `self`, and `-self`, extended `ioctl` and `nlmsg` ranges, conditionals, require/optional module blocks, user MLS ranges, all object context families, duplicate detection, platform rejection paths, and policy-version rejection paths.
