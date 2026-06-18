# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/__init__.py

## Purpose
This module is the main public query facade for the Python `sepolicy` package. It loads an installed or named SELinux binary policy via SETools, exposes normalized policy objects and rule searches, reads libselinux file-context and user mapping files, and provides higher-level helpers used by the CLI, generator, GUI, interface, boolean, communicate, network, and manpage layers.

## Important APIs and data
The module exports numeric info selectors (`TYPE`, `ROLE`, `ATTRIBUTE`, `PORT`, `USER`, `BOOLEAN`, `TCLASS`), rule selector strings (`ALLOW`, `AUDITALLOW`, `NEVERALLOW`, `DONTAUDIT`, `TRANSITION`, `ROLE_ALLOW`), query keys (`SOURCE`, `TARGET`, `PERMS`, `CLASS`), file-type display maps, default path-to-type mappings, and many cached query helpers.

Policy loading is centered on `_pol`. `get_installed_policy()` and `get_store_policy()` locate the highest-versioned `policy.N` file using `policy_sortkey()`. `policy(policy_file)` creates a `setools.policyrep.SELinuxPolicy` object and clears a subset of caches. `load_store_policy()`, `init_policy()`, and most query functions lazily initialize `_pol`.

`info(setype, name=None)` wraps SETools queries and returns generators of dictionaries for types, roles, attributes, ports, users, booleans, and object classes. `search(types, seinfo=None)` wraps `TERuleQuery` and `RBACRuleQuery`, normalizes rule objects through `_setools_rule_to_dict()`, and returns lists of dictionaries. Higher-level helpers derive conditionals, entrypoints, writable files, transitions, role allows, domains, roles, users, booleans, ports, file types, and boolean descriptions.

## Control flow
The common flow is lazy policy initialization, SETools query construction, conversion to plain dictionaries/strings, and optional cache storage. Rule queries are split by rule family: allow-like TE rules, transition-like TE rules, and role allow RBAC rules. File-context helpers read `file_contexts`, `.homedirs`, `.local`, `.subs`, and `.subs_dist`, normalize file class codes through `trans_file_type_str`, and build maps keyed by SELinux type or equivalence path.

Domain-oriented helpers compose lower-level data. For example, `get_writable_files(setype)` searches allow rules for `open` and `write`, expands attribute targets, filters to file types, and joins with file-context regex data. `get_bools(setype)` filters cached boolean rules for source domain and splits booleans into domain-specific and generic lists based on `gen_short_name()`. `get_entrypoints()`, `get_init_entrypoint*()`, and transition helpers bridge process transition rules to file-context path data.

## State and persistence
This module keeps extensive module-level caches: policy object, file equivalence maps, local file-context records, file-context dictionary, interface methods, type/domain/user/role/port/boolean/rule lists, and parsed boolean XML descriptions. These caches persist for the interpreter lifetime until `policy()` or `reinit()` clears them. Persistent external state is read from the host SELinux installation: binary policy files, file-context files, users configuration, active boolean states, file labels via `getfilecon`, and optional policy XML. The module itself does not write policy state.

## Dependencies and integration points
Runtime dependencies are `selinux`, SETools query classes, `sepolgen.defaults`, `sepolgen.interfaces`, `glob`, `gzip`, filesystem access, and optional `distro` for OS naming. Integration points include `generate.py` for policy module generation, `gui.py` for GTK display and DBus-driven changes, `interface.py` for interface metadata, and small CLI helpers such as `booleans.py` and `communicate.py`.

## Risks and edge cases
The global cache model is not thread-safe and can serve stale data after external semanage changes unless callers remember to call `reinit()`. `reinit()` sets `methods = None`, while `get_methods()` calls `len(methods)`, so calling `get_methods()` after `reinit()` can raise `TypeError`. `policy()` clears only some caches, leaving values such as `all_types_info`, file-context caches, login mappings, boolean XML dictionaries, and full rule caches potentially tied to a previous policy. Several helpers catch broad exceptions, hiding parsing or policy errors. `get_fcdict()` assumes base and homedir file-context files exist and raises if they do not. `gen_interfaces()` requires root when interface data is stale and exits indirectly through raised `ValueError`. XML parsing in `gen_bool_dict()` assumes description nodes exist. Rule dictionaries are loosely typed and callers must handle missing keys such as `permlist`, `transtype`, `booleans`, and `filename`.

## Test signals
Useful tests should cover policy path sorting, alias resolution in `get_real_type_name()`, `info()` result shapes for MLS and non-MLS policies, rule conversion for conditional and non-conditional rules, attribute expansion, file-context parsing including missing `.local` and `.subs` files, cache invalidation after `policy()` and `reinit()`, boolean description fallback, and behavior when SETools/libselinux calls raise. Integration tests should run against a small fixture policy or mocked SETools objects rather than a host policy only.
