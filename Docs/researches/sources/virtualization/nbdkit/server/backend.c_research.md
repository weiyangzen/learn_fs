# File Research: sources/virtualization/nbdkit/server/backend.c

Implements common backend registration, lifecycle, capability caching, and request dispatch wrappers for plugins and filters.

Key behavior:
- Debug flags `nbdkit.backend.controlpath` and `nbdkit.backend.datapath` control logging.
- `backend_init` initializes a backend object with magic, next pointer, stack index, type, filename copy, and dlopen handle.
- `backend_load` validates backend names, stores a copy, applies debug flags to the module, and calls optional load callback.
- `backend_unload` serializes unload with a global unload lock, calls optional unload, optionally `dlclose`s, and frees filename/name.
- `backend_list_exports` and `backend_default_export` wrap export enumeration/default export behavior, including TLS state and default export caching.
- `next_ops` provides the filter-facing `nbdkit_next_ops` table by mapping operations to backend wrapper functions.
- `backend_open` creates a context, handles shared/non-shared TLS state, resolves default export name for empty export, stores an exportname copy, calls the backend’s open, and manages inner context cleanup on failure.
- `backend_prepare` calls inner prepare first, then current prepare, setting `HANDLE_CONNECTED`.
- `backend_finalize` runs in reverse order and marks `HANDLE_FAILED` on failure.
- `backend_close` closes outer-to-inner, frees export name and context.
- `backend_valid_range` validates nonzero requests inside the negotiated export size.
- Control callbacks cache values on the context: export size, block size, write/flush/rotational/trim/zero/fast-zero/FUA/multi-conn/cache/extents capabilities.
- Capability wrappers enforce logical dependencies, such as trim/zero/FUA requiring write support, and fast zero requiring zero support.
- Datapath wrappers assert connection state, range validity, flags, and capability state before calling backend operations.
- `.zero` emulation writes static zero buffers in chunks, handles FUA emulation, and rejects fast-zero emulation with `ENOTSUP`.
- `.extents` falls back to one allocated-data extent when extents are unsupported.
- `.cache` emulation reads data into a static sink buffer.

Dependencies:
- `internal.h` backend/context definitions.
- nbdkit public API constants.
- dlopen/dlclose.
- protocol limits like `NBD_MAX_STRING`.

Notes and risks:
- Heavy use of `assert` means many invariants are developer/runtime assumptions rather than recoverable errors.
- Capability values are cached; plugins/filters should not change capability answers during a connection.
- Static buffers used for zero/cache emulation rely on the surrounding thread-safety guarantees and operation semantics.
