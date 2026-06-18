# sources/user-network-fs/samba/source3/rpc_client/py_mdscli.c

## Purpose
`py_mdscli.c` exposes Samba's mdssvc client helper API to Python as module `mdscli`. It wraps Spotlight/mdssvc connection, search, result retrieval, path lookup, search close, and disconnect operations around Python talloc objects.

## Important APIs, Types, And Functions
The module defines Python types `mdscli.conn` and `mdscli.ctx.search`. Connection methods are `sharepath()`, `search(pipe, query, basepath)`, and `disconnect(pipe)`. Search methods are `get_results(pipe)` and `close(pipe)`. Constructors are `conn_new()` and `search_new()`, and `MODULE_INIT_FUNC(mdscli)` registers both types. It uses `mdscli_connect/search/get_results/get_path/close_search/disconnect` async send/recv functions.

## Control Flow
Every method validates that `pipe` is a `samba.dcerpc.base.ClientConnection`, extracts the underlying `dcerpc_InterfaceObject`, retrieves the talloc-backed C context from `self`, starts the relevant mdssvc async request on `pipe->ev`, polls that same event context, then converts NTSTATUS failures to Python exceptions. `search_get_results()` loops while the server returns `NT_STATUS_PENDING`, sleeping one second between polls, then maps CNIDs to paths by issuing `mdscli_get_path_send()` for each result and appending Unicode strings to a Python list.

## State And Persistence
Python objects own `struct mdscli_ctx` and `struct mdscli_search_ctx` through pytalloc. No durable state is stored by this wrapper, but server-side mdssvc search contexts must be closed or disconnected through the wrapped API. Temporary talloc stackframes are freed on exit paths.

## Dependencies And Integration Points
Dependencies include Python C API, pytalloc, Samba Python module helpers, DCE/RPC Python utilities, tevent NTSTATUS polling, `cli_mdssvc.h`, and private mdssvc client structures. Build integration appears in `source3/wscript_build` as Python module `samba/samba3/mdscli.so`; command-line integration exists in `source3/utils/mdsearch.c` for the C client side.

## Risks
The wrapper deliberately avoids sync mdssvc helpers because Python DCE/RPC bindings use a specific event context; using the wrong context can hang. `search_get_results()` sleeps and repolls synchronously, which can block Python callers. Some paths raise through macros after allocating Python objects, so reference cleanup must remain careful. Constructors accept raw strings for share/mountpoint/query/basepath and depend on lower layers for semantic validation.

## Test Signals
Signals include Python import/type construction, invalid pipe type errors, mdssvc connect/search/result path mapping against a test share with Spotlight enabled, pending-result polling, no-more-matches handling, close/disconnect idempotence, and Python reference leak checks around error paths.
