# File Research: sources/virtualization/spdk/lib/rpc/rpc.c

This file implements SPDK’s core JSON-RPC method registry and Unix-domain RPC server wrapper.

Global state tracks the current RPC lifecycle state, whether duplicate/invalid method registration has occurred, and an optional allowlist. `spdk_rpc_set_state()` and `spdk_rpc_get_state()` manage startup/runtime state. Allowlisting is string-array based; if no allowlist is configured, all methods are allowed.

RPC methods are stored in a singly linked list with name, handler, state mask, deprecation/alias metadata, and one-shot deprecation warning state. `spdk_rpc_register_method()` rejects duplicate names and marks the registry incorrect. `spdk_rpc_register_alias_deprecated()` creates a deprecated alias for an existing non-alias method and rejects aliases of aliases. `spdk_rpc_verify_methods()` reports whether registration stayed clean.

`jsonrpc_handler()` finds the method by JSON string, applies the allowlist, resolves aliases, emits a deprecation warning once per deprecated alias, checks that the method’s state mask permits the current RPC state, and dispatches the handler. State failures return explanatory JSON-RPC invalid-state errors distinguishing startup-only and runtime-only calls.

`spdk_rpc_server_listen()` creates a Unix-domain JSON-RPC server. It validates the socket path, creates a `.lock` path, opens and exclusively locks it with `flock()`, unlinks any stale socket, and starts `spdk_jsonrpc_server_listen()`. The lock prevents multiple SPDK processes from using the same RPC socket. `spdk_rpc_server_accept()` polls the JSON-RPC server. `spdk_rpc_server_close()` unlinks socket and lock paths, shuts down the JSON-RPC server, closes the lock fd, and frees the wrapper.

Inspection helpers include `spdk_rpc_is_method_allowed()` and `spdk_rpc_get_method_state_mask()`. `spdk_rpc_set_allowlist()` replaces the global allowlist with a duplicated string array or clears it.

The built-in `rpc_get_methods` RPC optionally filters to currently callable methods and optionally includes aliases. It honors the allowlist and writes an array of method names. The built-in `spdk_get_version` RPC rejects params and returns the version string plus major/minor/patch/suffix fields and optional git commit.

Important invariants are method name uniqueness, alias resolution before state checking, allowlist enforcement in lookup and listing paths, and Unix socket lock cleanup on failure or close.
