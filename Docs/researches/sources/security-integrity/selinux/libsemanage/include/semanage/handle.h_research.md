# sources/security-integrity/selinux/libsemanage/include/semanage/handle.h

Purpose: declares the central libsemanage connection and transaction handle API. Every public database, module, debug, and policy operation flows through `semanage_handle_t`.

Important APIs/types/functions: defines `semanage_handle_t`, connection type enum values, handle create/destroy, store selection, connect/disconnect, begin transaction, commit, access checks, MLS query, root/store-root setters, reload/rebuild/check flags, dontaudit and tunable flags, default priority, compiler lookup, and module-cache controls.

Control flow: callers create a disconnected handle, optionally select a store and configure flags, connect to the backend, perform reads or begin writes, and commit or disconnect. Writer APIs may implicitly begin a transaction if one is not already held.

State and persistence behavior: the handle owns connection state, config, backend function table, locks, caches, message callback state, and commit options. Persistent effects occur only through backend commit/install logic; many setters just influence the next commit.

Dependencies and integration points: included by nearly all public headers and implemented by handle/direct API internals. It is the ABI boundary for direct store management, future policy server types, SWIG bindings, and command-line tools.

Risks: `semanage_handle_destroy` does not disconnect, so callers must disconnect connected handles first. Configuration setters have ordering constraints before connect. Test signals include connect/disconnect idempotence, lock acquisition, implicit transaction behavior, commit sequence numbers, flag effects on rebuild/reload, and access-check results.
