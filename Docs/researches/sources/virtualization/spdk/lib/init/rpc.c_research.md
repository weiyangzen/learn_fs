# File Research: sources/virtualization/spdk/lib/init/rpc.c

`rpc.c` manages framework RPC server instances during SPDK initialization/runtime. It supports multiple listen addresses, a shared poller that accepts connections on active servers, server pause/resume, and global finish cleanup.

Each `init_rpc_server` stores the RPC server object, listen address, active flag, and list link. `spdk_rpc_initialize()` validates registered RPC methods and options, rejects duplicate listen addresses, starts `spdk_rpc_server_listen()`, applies JSON-RPC log options, inserts the server into the global list, and registers the accept poller when the first server starts.

The accept poller walks all servers and calls `spdk_rpc_server_accept()` only for active ones. `spdk_rpc_server_pause()` and `spdk_rpc_server_resume()` toggle the active flag without closing the server.

`spdk_rpc_server_finish()` closes and removes one server by listen address, and unregisters the shared poller when no servers remain. `spdk_rpc_finish()` closes all servers. Option helpers provide size-versioned copy/default handling for `spdk_rpc_opts`, currently covering log file and log level with a static size assertion.

Research notes: all public functions assert app-thread execution. The global JSON-RPC log settings are only applied from opts for the first/default initialization path unless explicit opts are supplied.
