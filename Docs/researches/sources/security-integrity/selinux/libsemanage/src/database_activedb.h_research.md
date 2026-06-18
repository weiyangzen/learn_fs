# sources/security-integrity/selinux/libsemanage/src/database_activedb.h

Purpose: declares the generic active database adapter interface.

Important APIs/types/functions: defines `record_activedb_table_t` with `read_list` and `commit_list` callbacks, opaque `dbase_activedb_t`, init/release functions, and `SEMANAGE_ACTIVEDB_DTABLE`.

Control flow: object-specific code supplies callbacks, initializes an active database, and then uses normal generic database wrappers through the returned table.

State and persistence behavior: the adapter owns an in-memory list cache and delegates persistence to `commit_list`, usually affecting live kernel or process state rather than store files.

Dependencies and integration points: includes `database.h` and internal `handle.h`; used by active boolean support.

Risks: callback ownership of arrays and records must match the adapter's expectations. Test signals include backend init/release and full list commit behavior.
