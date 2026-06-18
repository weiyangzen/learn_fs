## sources/object-store/garage/src/api/k2v/index.rs

Purpose: implements K2V partition index listing and statistics response.

Important APIs/types/functions: `handle_read_index`, `ReadIndexResponse`, and `ReadIndexResponseEntry`.

Control flow: resolves all non-gateway node IDs from cluster layout, calls `read_range` over `garage.k2v.counter_table.table` with optional prefix/start/end/limit/reverse and a not-deleted filter scoped to those nodes, then maps per-partition counters (`entries`, `conflicts`, `values`, `bytes`) from filtered values into JSON response fields with pagination flags.

State/persistence: read-only access to K2V counter table and cluster layout.

Dependencies/integration: depends on K2V counter constants (`ENTRIES`, `CONFLICTS`, `VALUES`, `BYTES`), table range utility, and common JSON response helper.

Risks: cluster layout lookup can fail and affects filtered counter values. Counter names are stringified constants; mismatches would silently return zero defaults. Pagination semantics are inherited from `read_range`.

Test signals: no local tests; range utility and K2V API integration should cover response shape and pagination.
