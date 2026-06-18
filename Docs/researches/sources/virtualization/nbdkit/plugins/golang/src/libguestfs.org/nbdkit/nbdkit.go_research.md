# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/nbdkit.go

This is the main Go binding layer that lets Go code implement nbdkit plugins.

Public API:
- Defines `PluginInterface` for lifecycle/config/open callbacks.
- Defines `ConnectionInterface` for per-connection size, read, write, flush, trim, zero, multi-conn, rotational, and close callbacks.
- Provides default `Plugin` and `Connection` structs with no-op or conservative implementations.
- Exposes nbdkit constants for thread models, flags, FUA, cache, extents, and API version.
- Defines `PluginError` to carry an error message and optional errno.

C/Go bridge:
- Exported `impl*` functions convert C callbacks into Go method calls.
- Connections are stored in a global `map[uintptr]ConnectionInterface`, protected by a mutex.
- `implOpen` assigns nonzero integer handles cast to pointers.
- `implPRead` and `implPWrite` wrap C memory as Go `[]byte` using `reflect.SliceHeader` and `unsafe`.
- `PluginInitialize` builds a C `struct nbdkit_plugin`, fills callback pointers from C wrappers, mallocs a permanent copy, and returns it.

Important behavior:
- The binding sets thread model to parallel in the plugin struct.
- Go plugins are marked as not preserving errno.
- `set_error` maps `PluginError` through `nbdkit_set_error` and `nbdkit_error`.

Risks:
- Uses unsafe slice construction over C buffers.
- Connection handle IDs are pointer-shaped integers, requiring nonzero start.
- Some locking uses exclusive `Lock` where `RLock` would suffice, but correctness is maintained.
- `PluginError.String` appears inverted: it prints errno text when `Errno == 0`, likely contrary to intent.
