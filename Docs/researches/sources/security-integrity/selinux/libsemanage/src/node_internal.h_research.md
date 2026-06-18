# sources/security-integrity/selinux/libsemanage/src/node_internal.h

Purpose: declares internal network-node record hooks.

Important APIs: `SEMANAGE_NODE_RTABLE`, `node_file_dbase_init/release`, `node_policydb_dbase_init/release`, `semanage_node_validate_local`, and `semanage_node_compare2_qsort`.

Control flow/integration: local stores use the file backend; policy views use the policydb backend; qsort comparator supports sorted node handling, especially during merge or validation paths.

State/persistence: no state in the header. Persistent data is in local node text stores and policydb. Risks include a declared `semanage_node_validate_local` without an implementation in the listed `nodes_local.c`, which should be checked elsewhere in the tree or build. Test signals include compile/link coverage and node parser/policydb CRUD.
