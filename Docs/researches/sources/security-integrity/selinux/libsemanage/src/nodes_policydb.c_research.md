# sources/security-integrity/selinux/libsemanage/src/nodes_policydb.c

Purpose: connects node records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_NODE_POLICYDB_RTABLE`, `node_policydb_dbase_init`, and release. The table maps modify/query/count/exists/iterate to `sepol_node_*`.

Control flow: initialization supplies active/tmp kernel policy paths, the node record table, and policydb operation table to `dbase_policydb_init`, then sets `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: participates in active/tmp policydb transaction handling. Risks include unsupported add/set operations and dependence on correct semanage store path setup. Tests should cover init/release, policy list/count, and local node merge with sorted ordering.
