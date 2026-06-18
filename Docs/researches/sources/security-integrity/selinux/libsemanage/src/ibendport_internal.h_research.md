# sources/security-integrity/selinux/libsemanage/src/ibendport_internal.h

Purpose: declares internal hooks for InfiniBand end port records. It connects public ibendport APIs to record, file, local, and policydb backends.

Important APIs: `SEMANAGE_IBENDPORT_RTABLE`, `ibendport_file_dbase_init/release`, `ibendport_policydb_dbase_init/release`, `semanage_ibendport_validate_local`, and `semanage_ibendport_compare2_qsort`.

Control flow/integration: file-store initialization is used for local modifications; policydb initialization binds to the active/tmp kernel policy; local validation detects duplicate end-port entries; qsort comparator supports validation ordering.

State/persistence: no state in the header. Persistent state lives in local ibendport text stores and kernel policydb views. Risks are stale declarations versus implementation and missing validation invocation before commit. Test signals include compile coverage, duplicate ibdev/port rejection, and policydb query/list operations.
