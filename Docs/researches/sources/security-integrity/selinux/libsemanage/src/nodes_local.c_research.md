# sources/security-integrity/selinux/libsemanage/src/nodes_local.c

Purpose: local network-node CRUD wrappers over the handle's local node database.

Important APIs: `semanage_node_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local`.

Control flow: each function selects `semanage_node_dbase_local(handle)` and delegates to generic database operations. There is no overlap or context validator in this file.

State/persistence: local node records are modified/read and later flushed by commit components. Integration is with `policy_components.c`, which sorts node local records before merging into policy.

Risks: any declared local validation must be implemented elsewhere or not linked; this file itself performs no validation beyond generic database semantics. Test signals include local modify/query/delete/list and commit merge ordering for node records.
