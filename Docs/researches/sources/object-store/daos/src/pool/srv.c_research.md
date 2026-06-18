# sources/object-store/daos/src/pool/srv.c

## Purpose

This file is the DAOS pool server module registration unit. It wires the pool subsystem into the DAOS server module framework, initializes and tears down global pool-server facilities, registers RPC handlers for supported pool protocol versions, creates per-xstream pool TLS, and attaches module metrics. It is not where most pool operations are implemented; instead it orchestrates `srv_pool.c`, `srv_target.c`, `srv_iv.c`, `srv_layout.c`, and `srv_metrics.c` through declarations in `srv_internal.h`.

## Important APIs, types, and functions

- Globals: `ec_agg_disabled`, `pw_rf`, and `ps_cache_intvl`.
- `check_pool_redundancy_factor()`: parses and validates `DAOS_POOL_RF`.
- `init()` / `fini()`: module lifecycle for pool cache, handle hash, IV classes, default properties, replicated service class, and BIO reaction ops.
- `setup()` / `cleanup()`: protocol setup, optional pool startup, and pool stop.
- `pool_tls_init()` / `pool_tls_fini()`: per-xstream `struct pool_tls` lifecycle.
- `pool_handlers_v6` / `pool_handlers_v7`: protocol-specific RPC handler tables.
- `pool_module_key`, `pool_metrics`, and `pool_module`: framework descriptors consumed by DAOS server startup.

## Control flow

Startup proceeds through `pool_module.sm_init` then `pool_module.sm_setup`. `init()` is ordered defensively: cache init, handle hash init, IV class registration, default property initialization, environment processing, replicated service registration, and BIO reaction registration. Each intermediate failure jumps to a label that undoes only already-initialized subsystems. `setup()` computes the pool RPC protocol version from the engine join version and starts all pools unless the engine is in check mode or `DAOS_START_POOLS` disables startup. Shutdown calls `cleanup()` for live pools and `fini()` for global state.

## State and persistence behavior

This file owns process/module state, not durable pool metadata. Persistent storage is delegated to `srv_layout.c`/`srv_pool.c`; distributed cache state is delegated to `srv_iv.c`. The persistent side effect of `setup()` is indirect: `ds_pool_start_all()` loads and starts services from RDB-backed pool state. TLS state is transient per xstream and expected to be empty by finalization.

## Dependencies and integration points

It depends on DAOS server module APIs, CART RPC protocol registration, BIO reaction hooks, metrics registration, environment parsing, and pool internal APIs declared in `srv_internal.h`. It integrates with `srv_iv.c` through IV init/fini, `srv_layout.c` through default property init/fini, target/pool service code through cache/hash/start/stop calls, and `srv_metrics.c` through `pool_metrics`.

## Risks and test signals

Initialization order matters; failure injection should verify each cleanup label. `pw_rf` uses `(uint32_t)-1` as a sentinel. TLS finalization logs leaked child references unless `DAOS_STRICT_SHUTDOWN` asserts. Tests should cover environment parsing, check-mode startup, `DAOS_START_POOLS=false`, strict shutdown, and handler table compatibility for protocol v6/v7.
