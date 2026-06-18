# sources/security-integrity/selinux/libsemanage/include/semanage/interfaces_local.h

Purpose: declares the local-store CRUD surface for `network interface` records. These functions operate on administrator overrides in the writable semanage store rather than directly exposing the compiled policy view.

Important APIs/types/functions: exports `semanage_iface_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local` over ``semanage_iface_key_t`` and ``semanage_iface_t`` values. The list/query APIs allocate records for the caller to free with the matching record free routine.

Control flow: callers create or extract a key, optionally begin a transaction, call the local operation, and commit through `semanage_commit`. The implementation routes through the handle's local `dbase_config_t` and the generic database wrappers, so cache loading and transaction entry happen below this header.

State and persistence behavior: modify/delete calls affect local customization files under the direct store sandbox and are made durable only after the enclosing semanage commit installs the sandbox. Query/count/list read the cached local database and do not change persistent policy state.

Dependencies and integration points: depends on `semanage/handle.h` and the corresponding record header. It integrates with direct API component commits, local file databases, validators, and tools such as `semanage` that manage overrides.

Risks: the API assumes callers pass keys matching the record identity and manage returned allocations. Missing transaction discipline can leave writes cached but not installed. Test signals are local override add/delete/query scenarios, commit/reload behavior, and validation failures for malformed or overlapping local records.
