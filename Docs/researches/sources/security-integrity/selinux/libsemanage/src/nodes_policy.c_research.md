# sources/security-integrity/selinux/libsemanage/src/nodes_policy.c

Purpose: policy-view read APIs for network node records.

Important APIs: `semanage_node_query`, `exists`, `count`, `iterate`, and `list`.

Control flow: thin wrappers select `semanage_node_dbase_policy(handle)` and call generic database routines.

State/persistence: reads policydb-backed node data. It does not mutate stores.

Dependencies/integration: public semanage node APIs and Python tests use this layer to inspect node contexts. Risks are use before connection and absent policydb backend setup. Test signals include list/query/count on IPv4 and IPv6 nodecon policies.
