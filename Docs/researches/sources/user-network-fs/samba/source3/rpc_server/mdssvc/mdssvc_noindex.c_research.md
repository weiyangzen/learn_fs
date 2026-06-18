# sources/user-network-fs/samba/source3/rpc_server/mdssvc/mdssvc_noindex.c

Purpose: implements the fallback mdssvc backend for shares with Spotlight enabled but no real search index. It satisfies the backend contract while returning no indexed search results.

Important APIs and functions: `mdssvc_noindex_init()`, `mdssvc_noindex_shutdown()`, and `mds_noindex_connect()` all return success without allocating persistent state. `mds_noindex_search_start()` and `mds_noindex_search_cont()` set the common `sl_query` state to `SLQ_STATE_DONE`, causing fetches to return an empty completed result set. `mdsscv_backend_noindex` exports these callbacks.

Control flow: when `mds_init_ctx()` selects `SPOTLIGHT_BACKEND_NOINDEX`, query open still parses request metadata and creates common result structures. The backend immediately marks the query done. Client fetch then runs through normal serialization in `mdssvc.c`, which includes the usual status/result container but no paths.

State and persistence: no backend-private state is created. All state remains in the common query object and is freed by normal mdssvc close/timeout/destructor paths.

Dependencies: only `includes.h` and `mdssvc.h`. This makes it a low-risk baseline implementation and a useful fallback for builds without ES support.

Risks: because this backend reports successful empty searches, clients may see Spotlight capability but no search matches. That is intentional but can mask configuration mistakes if administrators expected ES indexing.

Test signals: basic mdssvc RPC tests should verify noindex open/fetch/close success, `DONE` state, empty CNID arrays, and no backend-private allocations.
