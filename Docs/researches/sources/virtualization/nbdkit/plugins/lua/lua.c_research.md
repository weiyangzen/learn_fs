# File Research: sources/virtualization/nbdkit/plugins/lua/lua.c

This file implements the nbdkit Lua language plugin, forwarding nbdkit callbacks into functions defined by a Lua script.

Lifecycle/config:
- Creates a global Lua interpreter in `.load` and opens standard libraries.
- Requires the first parameter to be `script=<path>`.
- Loads and runs the Lua script during config.
- Requires Lua functions `open`, `get_size`, and `pread`.
- Subsequent config keys are forwarded to Lua `config` if defined.
- `config_complete` forwards to Lua `config_complete` if defined.
- `dump_plugin` prints Lua version and optionally calls Lua `dump_plugin`.

Handle model:
- `open` calls Lua `open(readonly)` and stores the returned Lua object in the registry.
- The C handle is an allocated integer registry reference.
- `close` optionally calls Lua `close(handle)`, then unreferences the Lua object.

I/O and capabilities:
- `get_size` expects integer/number result.
- `pread` expects a string at least as long as requested.
- `pwrite`, `flush`, `trim`, and `zero` call matching Lua functions when available.
- `can_write`, `can_flush`, `can_trim`, and `is_rotational` call Lua capability functions when available.
- If `pwrite`, `flush`, or `trim` exists without a matching `can_*`, capability defaults to enabled for write/flush/trim.
- `zero` falls back with `EOPNOTSUPP` if no Lua zero function exists.

Threading:
- Uses `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`, appropriate for a single global Lua state.

Compatibility:
- Provides a fallback `lua_isinteger` for Lua versions lacking it.

Risks:
- One global Lua state means all scripts/connections share interpreter state.
- Lua callback type validation is strict but simple.
- `can_flush` checks for `plugin_flush` in one fallback branch, while the actual callback name is `flush`; this looks suspicious.
