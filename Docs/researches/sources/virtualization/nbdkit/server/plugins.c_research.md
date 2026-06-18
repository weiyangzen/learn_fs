# File Research: sources/virtualization/nbdkit/server/plugins.c

Purpose: Adapts a loaded `struct nbdkit_plugin` into the internal backend vtable, including capability normalization, old API compatibility, error capture, and operation emulation.

Structure:
- `struct backend_plugin` embeds `struct backend` plus a copied `struct nbdkit_plugin`.
- `plugin_register` initializes the backend, calls `plugin_init`, validates API version and required callbacks, copies only the plugin-declared struct size for ABI compatibility, then runs backend load.

Required callbacks:
- `.open`
- `.get_size`
- `.pread` or legacy `._pread_v1`

Lifecycle/config:
- Implements plugin free, thread model selection, name, usage, version, dump fields, config, config_complete, magic config key, get_ready, after_fork, cleanup, preconnect, list_exports, default_export, open/prepare/finalize/close.
- Plugins do not receive internal prepare/finalize callbacks; those are no-ops because plugin `.open`/`.close` can cover the same need.

Thread model:
- Starts from plugin `_thread_model`.
- If the platform lacks atomic CLOEXEC primitives, downgrades overly parallel models to `serialize_all_requests` to avoid fd leaks.
- Plugin-provided `thread_model` can further restrict concurrency.

Capabilities:
- Boolean-style plugin callbacks are normalized to `0`, `1`, or `-1`.
- Defaults infer write/flush/trim/zero/extents/cache support from presence of operation callbacks.
- `can_zero` maps public boolean semantics to internal native/emulate states.
- `can_fua` respects API version: API v1 cannot receive native FUA even if it reports it.
- `can_fast_zero` advertises fast failure where native zero support is absent.

Error handling:
- `nbdkit_set_error(err)` stores plugin-provided errno in thread-local state.
- `get_errno` uses thread-local error, preserved `errno` when the plugin opts in, or `EIO` fallback.

Data operations:
- `plugin_pread`, `plugin_pwrite`, `plugin_flush`, `plugin_trim`, `plugin_zero`, `plugin_extents`, and `plugin_cache` translate internal backend calls to plugin callbacks.
- FUA is emulated with a follow-up flush when native FUA is unavailable.
- Zero requests prefer native `.zero`; on unsupported non-fast zero, they emulate by writing static zero buffers through `plugin_pwrite`.
- Fast zero returns `EOPNOTSUPP` when unsupported rather than falling back to slow writes.
- `plugin_extents` rejects successful callbacks that return no extents.
- `plugin_cache` treats advertised cache without `.cache` as a no-op.

Dump support:
- `plugin_dump_fields` prints path, name, version, API version, struct size, max/effective thread model, errno behavior, magic key, presence bits for callbacks, and custom plugin dump output.
