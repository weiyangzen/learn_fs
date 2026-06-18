# File Research: sources/virtualization/nbdkit/plugins/golang/examples/ramdisk/ramdisk.go

This Go example implements a shared in-memory writable RAM disk.

Key behavior:
- Requires `size` configuration.
- `GetReady` allocates a global `[]byte` of the requested size.
- `Open` returns a stateless connection.
- `GetSize` returns the configured size.
- `PRead` and `PWrite` copy to/from the global byte slice.
- `CanWrite` enables writes.
- `CanMultiConn` returns true because all clients share the same backing slice.

Risks:
- No explicit locking around the shared byte slice; safety depends on nbdkit/threading expectations and Go runtime behavior for concurrent slice access.
- Offset conversion mixes `uint64` and `int`, which can overflow on very large sizes.
