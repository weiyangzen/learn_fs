# sources/security-integrity/selinux/libsemanage/src/handle.h

Purpose: defines the internal `struct semanage_handle`, database slot numbering, and inline selectors for local, policy, homedir, and active databases.

Important types/macros: `DBASE_COUNT` is 24. Slot macros distinguish local modifications (`DBASE_LOCAL_*`), policy plus local merged views (`DBASE_POLICY_*`), generated homedir fcontexts, and active booleans. The handle contains error callback fields, direct backend union, `sepolh`, parsed config, priority, connection/transaction flags, policy options, backend function table, and `dbase_config_t dbase[DBASE_COUNT]`.

Control flow/integration: nearly every local/policy API uses the inline selectors in this header to obtain the correct `dbase_config_t` before delegating to `dbase_*`. Backend connection initializes these slots; commit code flushes and merges selected slots.

State/persistence: this header defines the in-memory state graph that mediates persistent local store files, policydb views, and active kernel policy state. It does not allocate or free itself.

Risks: slot order is a hard internal contract; adding a database requires updating `DBASE_COUNT`, selectors, backend initialization, merge/flush lists, and tests. Test signals are broad integration tests for each object family and compile warnings that catch selector/slot mismatches.
