# sources/security-integrity/selinux/libsemanage/src/ibpkeys_policydb.c

Purpose: binds ibpkey records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_IBPKEY_POLICYDB_RTABLE`, `ibpkey_policydb_dbase_init`, and `ibpkey_policydb_dbase_release`. The table maps modify/query/count/exists/iterate to `sepol_ibpkey_*`.

Control flow: initialization calls `dbase_policydb_init` with active/tmp kernel policy paths, `SEMANAGE_IBPKEY_RTABLE`, and the policydb operation table, then sets `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: participates in policydb transaction state, reading active policy and writing/modifying the tmp policy during merges. Risks are unsupported add/set table entries and path misconfiguration. Tests should cover backend init/release and local ibpkey merge into policydb during commit.
