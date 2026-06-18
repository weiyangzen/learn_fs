# sources/security-integrity/selinux/libsemanage/src/database.h

Purpose: defines libsemanage's generic record and database polymorphism interfaces.

Important APIs/types/functions: declares opaque `record_t`, `record_key_t`, and `dbase_t`; `record_table_t` for create/key/compare/clone/free operations; `dbase_table_t` for CRUD, iteration/listing, cache/drop/flush, modification status, and record-table retrieval; `dbase_config_t`; and generic wrapper prototypes.

Control flow: each object/backend pair supplies record and database method tables. Public object APIs call the generic wrappers with a configured backend, which call method-table operations after cache/transaction setup.

State and persistence behavior: the header specifies ownership: keys and input data remain caller-owned, query/list results become caller-owned, and caches belong to backends. Persistence semantics are delegated to each backend's `flush` implementation.

Dependencies and integration points: included by every backend and internal object implementation. It is the architectural center that lets booleans, users, ports, nodes, and other records share file, policydb, join, and active database logic.

Risks: method tables are ABI-internal but semantically strict; a bad comparator or clone routine can corrupt list ordering or ownership. Test signals include generic CRUD conformance across all backends and memory ownership under error paths.
