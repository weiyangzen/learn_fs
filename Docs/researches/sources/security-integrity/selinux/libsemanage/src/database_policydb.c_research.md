# sources/security-integrity/selinux/libsemanage/src/database_policydb.c

Purpose: implements a generic policydb backend, adapting object-specific libsepol policydb operations to the semanage database interface.

Important APIs/types/functions: cache/drop/set-serial/needs-resync/flush/init/release/attach/detach helpers; generic add/set/modify/delete/clear/query/exists/count/iterate/list operations; `SEMANAGE_POLICYDB_DTABLE`.

Control flow: cache creates and reads a `sepol_policydb_t` from paths when not attached, iterates object records into the linked-list cache, and tracks serials. During commit, attach binds the backend to a shared output policydb; operations call record policydb callbacks and update the cache. Detach drops attachment state.

State and persistence behavior: owns optional cached policydb, linked-list cache, modification flag, path references, and attach state. Flush writes changes into the policydb object; writing policy files is handled elsewhere.

Dependencies and integration points: depends on libsepol policydb APIs, generic linked-list caching, semanage path/serial logic, and object-specific `record_policydb_table_t` implementations.

Risks: attached mode intentionally prevents normal drop/flush assumptions; incorrect detach could leave dangling policydb pointers. Test signals include file-backed policy reads, attached merge behavior, count/list/query accuracy, and resync after commit serial changes.
