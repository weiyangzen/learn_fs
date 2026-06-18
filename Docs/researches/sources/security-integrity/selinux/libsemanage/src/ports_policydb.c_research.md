# sources/security-integrity/selinux/libsemanage/src/ports_policydb.c

Purpose: binds port records to libsepol policydb operations.

Important APIs/functions: `SEMANAGE_PORT_POLICYDB_RTABLE`, `port_policydb_dbase_init`, and release. The table maps modify/query/count/exists/iterate to `sepol_port_*`.

Control flow: initialization calls `dbase_policydb_init` with active/tmp kernel policy paths, `SEMANAGE_PORT_RTABLE`, and policydb operation table, then sets `SEMANAGE_POLICYDB_DTABLE`.

State/persistence: reads active policy and modifies temporary policy during transaction merge. Risks include unsupported add/set operations and dependence on correct store path initialization. Tests should cover backend init/release, policy list/count, and local port merge after validation.
