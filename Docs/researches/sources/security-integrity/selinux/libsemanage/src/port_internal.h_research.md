# sources/security-integrity/selinux/libsemanage/src/port_internal.h

Purpose: declares internal network-port record hooks.

Important APIs: `SEMANAGE_PORT_RTABLE`, `port_file_dbase_init/release`, `port_policydb_dbase_init/release`, `semanage_port_validate_local`, and `semanage_port_compare2_qsort`.

Control flow/integration: file backend parses local `portcon` records; policydb backend binds to libsepol; local validator uses qsort comparator to reject overlaps before merge.

State/persistence: no state. Persistent records live in local port text stores and policydb. Risks are declaration drift and missing validation invocation. Test signals include parser round-trip, overlap validation, and policydb list/query.
