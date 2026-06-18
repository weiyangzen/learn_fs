# sources/security-integrity/selinux/libsemanage/include/semanage/ibendports_policy.h

Purpose: declares read-only accessors for `InfiniBand end-port` records as seen in the policy database. This is the policy/base view paired with the writable local override API.

Important APIs/types/functions: exports `semanage_ibendport_query`, `exists`, `count`, `iterate`, and `list` over ``semanage_ibendport_key_t`` and ``semanage_ibendport_t``. The APIs use `semanage_handle_t` for backend selection and return cloned record objects owned by the caller.

Control flow: after `semanage_connect`, callers create a key or enumerate the database. The implementation forwards to the policy `dbase_config_t`, which may read a policy file or attach to an in-memory `sepol_policydb_t` during commit.

State and persistence behavior: these calls are observational. They populate or reuse database caches but do not write local files or the installed policy. Returned lists are snapshots, not live database views.

Dependencies and integration points: depends on the object record header and the semanage handle. It is consumed by management tools, SWIG bindings, validators, and direct commit merge code that needs to compare local overrides against base policy state.

Risks: iteration callbacks cannot safely mutate the underlying database and must clone records they retain. Test signals include query/list/count parity with policy contents, callback early-exit behavior, allocation cleanup, and accurate visibility after policy rebuilds.
