# sources/security-integrity/selinux/libsemanage/src/database_join.h

Purpose: declares the generic virtual join database interface.

Important APIs/types/functions: defines placeholder `record1_t` and `record2_t`, opaque `dbase_join_t`, `record_join_table_t` callbacks `join` and `split`, `dbase_join_init`, `dbase_join_release`, and `SEMANAGE_JOIN_DTABLE`.

Control flow: object-specific code supplies two component database configs and callbacks that can combine or split records. Generic database wrappers then expose the joined view as if it were a normal database.

State and persistence behavior: the join database caches synthesized records; persistent writes are delegated back into the two component databases on flush.

Dependencies and integration points: includes `database.h` and `handle.h`. It supports composite record models while preserving existing file/policydb backends.

Risks: callbacks must tolerate NULL component records and preserve key ordering. Test signals include joins with missing left/right sides and successful split persistence.
