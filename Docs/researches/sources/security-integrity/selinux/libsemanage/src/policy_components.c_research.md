# sources/security-integrity/selinux/libsemanage/src/policy_components.c

Purpose: merges local component databases into the policy database and flushes component databases during commit.

Important functions: `clear_obsolete`, `load_records`, `semanage_base_merge_components`, and `semanage_commit_components`. Mode flags are `MODE_SET`, `MODE_MODIFY`, and `MODE_SORT`.

Control flow: base merge iterates an ordered component table: users, ports, interfaces, booleans, seusers, nodes, ibpkeys, and ibendports. It caches source/destination databases, lists local records, optionally sorts records, clears obsolete destination entries for set-style booleans, then loads each record via set or modify. Commit components flushes local/policy/active database slots in a fixed order and drops caches on failure.

State/persistence: merge mutates the temporary policydb view; commit flushes local and active stores. Ordering matters because records can have policy dependencies. Dependencies include handle database selectors, generic database tables, module definitions, and debug logging.

Risks: the component arrays are hard-coded and must be updated when new database slots are added. Error paths rely on table-specific key/free semantics. Tests should cover local boolean obsolete clearing, sorted node merge, port/ibpkey overlap validation before merge, flush failure cache dropping, and commit with each component family.
