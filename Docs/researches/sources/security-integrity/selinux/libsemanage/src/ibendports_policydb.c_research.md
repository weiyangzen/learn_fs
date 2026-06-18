# sources/security-integrity/selinux/libsemanage/src/ibendports_policydb.c

Purpose: binds InfiniBand end-port records to the libsepol policydb backend.

Important APIs/functions: `SEMANAGE_IBENDPORT_POLICYDB_RTABLE`, `ibendport_policydb_dbase_init`, and `ibendport_policydb_dbase_release`. The policydb table maps modify/query/count/exists/iterate to `sepol_ibendport_*`.

Control flow: initialization calls `dbase_policydb_init` with active and temporary kernel policy paths, the ibendport record table, and the ibendport policydb operation table, then sets `dconfig->dtable` to `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: reads from `SEMANAGE_ACTIVE/SEMANAGE_STORE_KERNEL` and writes/merges against `SEMANAGE_TMP/SEMANAGE_STORE_KERNEL` during transactions. Risks include path selection errors and lack of `.add`/`.set` entries, so callers must use supported modify semantics. Test signals include policydb initialization, list/count, and local merge through `semanage_base_merge_components`.
