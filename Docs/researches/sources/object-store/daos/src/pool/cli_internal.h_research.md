# sources/object-store/daos/src/pool/cli_internal.h

Purpose: internal declarations for the pool client implementation shared across pool client compilation units.

Important APIs and types: declares `dc_pool_hdl_link()`, `dc_pool_hdl_unlink()`, `dc_pool_alloc()`, and `dc_pool_map_update()`. Defines `struct dc_pool_tls` with a mutex and list for per-thread pool metrics. Declares `dc_pool_module_key` and inline `dc_pool_tls_get()` to retrieve pool TLS via DAOS module-key TLS.

Control flow: `dc_pool_tls_get()` obtains DAOS thread-local storage for the module key tags, asserts it exists, and returns the module-specific data pointer.

State and persistence: defines TLS structure only; runtime ownership is in `cli.c` initialization/finalization callbacks. No persistence.

Dependencies and integration: depends on `struct dc_pool`, `struct pool_map`, DAOS TLS, DAOS module key, pthread mutexes, and DAOS intrusive lists. It is tightly coupled to `cli.c` metrics and map update internals.

Risks: `dc_pool_tls_get()` asserts on missing TLS rather than returning NULL, so callers must only use it after module/TLS registration. The header exposes internal handle and map update functions, so misuse outside intended pool client internals could bypass lifecycle rules.

Test signals: compile-time signal is that pool client files share the same internal prototypes; runtime metrics tests should show valid TLS after `dc_pool_init()` when client metrics are enabled.
