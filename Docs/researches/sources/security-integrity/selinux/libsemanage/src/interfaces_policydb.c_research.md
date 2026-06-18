# sources/security-integrity/selinux/libsemanage/src/interfaces_policydb.c

Purpose: connects interface records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_IFACE_POLICYDB_RTABLE`, `iface_policydb_dbase_init`, and `iface_policydb_dbase_release`. It maps modify/query/count/exists/iterate to `sepol_iface_*`.

Control flow: initialization passes active and temporary kernel policy paths to `dbase_policydb_init` along with interface record and policydb operation tables, then sets the database table to `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: policydb transaction state is handled by the generic policydb backend. Risks include typo-level comments only, unsupported add/set operations, and dependency on correct semanage store paths. Tests should initialize/release the backend and merge local interface modifications into tmp policydb.
