# sources/security-integrity/selinux/libsemanage/src/ibpkeys_policy.c

Purpose: provides policy-view read APIs for InfiniBand P_Key records.

Important APIs: `semanage_ibpkey_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: each function retrieves `semanage_ibpkey_dbase_policy(handle)` and delegates to the generic database operation.

State/persistence: reads from the policydb-backed ibpkey database initialized for the handle. It does not mutate stores.

Dependencies/integration: public libsemanage APIs and any bindings use this layer to inspect policy P_Key contexts. Risks are missing handle connection or backend setup. Test signals include list/count/query with policy records and behavior on absent keys.
