# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_es.h

Purpose: declares private state structures and the exported backend vtable for the Elasticsearch mdssvc backend.

Important APIs and types: `struct mdssvc_es_ctx` is process/global backend state with the owning `mdssvc_ctx`, anonymous HTTP credentials, loaded Jansson mapping tree, and default ES search fields. `struct mds_es_ctx` is per RPC bind/share state with a pointer back to `mds_ctx`, a pointer to global ES state, an HTTP connection, and queued searches. `struct sl_es_search` is per query request state with dlist links, pending flag, event context, owning bind state, parent `sl_query`, result totals, paging fields, and the translated ES query string. `mdsscv_backend_es` is exported for selection by `mds_init_ctx()`.

Control flow and integration: the types mirror the backend contract in `mdssvc.h`. `mds_ctx->backend_private` points at `mds_es_ctx`; `sl_query->backend_private` points at `sl_es_search`. The queue/pending fields support serialized HTTP use while retaining multiple client query cursors.

State and persistence: only the mapping JSON and default field string are process-level state. Search cursors are per bind and per query. Persistent metadata lives outside Samba in Elasticsearch.

Dependencies: includes Jansson and assumes mdssvc core types are visible from including translation units. Consumers must also link against the generated parser/mapping support used by `mdssvc_es.c`.

Risks: the header exposes raw pointers for async state without locking primitives; lifetime is governed by talloc parentage and destructors in the C file. Any future concurrent HTTP dispatch would need stronger invariants around `pending`, list head ordering, and `slq` nulling.

Test signals: compile tests should catch backend-vtable availability under `HAVE_SPOTLIGHT_BACKEND_ES`; runtime tests need to inspect transitions of `mds_ctx->backend_private` and `sl_query->backend_private`.
