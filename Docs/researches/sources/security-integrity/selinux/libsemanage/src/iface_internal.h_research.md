# sources/security-integrity/selinux/libsemanage/src/iface_internal.h

Purpose: declares internal network interface record hooks.

Important APIs: `SEMANAGE_IFACE_RTABLE`, `iface_policydb_dbase_init/release`, `iface_file_dbase_init/release`.

Control flow/integration: the file backend parses local `netifcon` records; the policydb backend exposes policy records; local and policy wrappers use the record table for generic database operations.

State/persistence: no state. Persistent data lives in local interface text stores and policydb records. Risks are missing a local validation hook compared with ports/ibpkeys; context validity is mainly enforced by parsing/policydb checks. Test signals include file parser round-trip and policy/local CRUD.
