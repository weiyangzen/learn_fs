# sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_state.c

Purpose: persistent storage layer for FSRVP server state, serializing and reconstructing the shadow copy set hierarchy in `srv_fss.tdb`.

Important APIs/types/functions: `fss_state_store`, `fss_state_retrieve`, `fss_state_sc_set_store`, `fss_state_sc_store`, `fss_state_smap_store`, matching retrieve helpers, `fss_state_retrieve_traverse`, and hierarchy rebuild helpers for sets, copies, and share maps.

Control flow: store opens/creates the TDB read-write, wipes existing contents, stores the version and set count, starts a transaction, and writes each set, child snapshot, and share map under path-like keys such as `sc_set/<set>/sc/<copy>/smap/<share>`. Retrieve opens read-only, validates the database version, traverses every record into flat lists based on key prefixes, then reconstructs parent-child ownership by matching key-path substrings and trimming keys down to GUID/share-name components.

State/persistence behavior: all persisted payloads are generated `fsrvp_state_*` NDR blobs. Empty optional fields such as uncommitted `sc_path` or missing comments are stored as empty strings and restored as `NULL`. The database is all-or-rewritten on every store.

Dependencies/integration: uses dbwrap/TDB, generated `ndr_fsrvp_state`, talloc ownership moves, GUID parsing, NTSTATUS mapping, and private FSS structures.

Risks/test signals: hierarchy reconstruction uses substring membership tests on stored key paths, so malformed keys can create false parent matches unless counts catch it. The traverse prefix checks are order-sensitive because `smap` keys also contain `sc`. Tests should cover missing DB as success-empty, unsupported version, corrupt NDR payloads, orphan records, inconsistent child counts, all state enum values, and atomic transaction failure paths.
