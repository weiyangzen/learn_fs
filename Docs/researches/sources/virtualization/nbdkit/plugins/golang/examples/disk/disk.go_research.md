# File Research: sources/virtualization/nbdkit/plugins/golang/examples/disk/disk.go

This Go example implements a per-client temporary writable disk.

Key behavior:
- Requires `size` config and parses it with `strconv.ParseUint`.
- `Open` creates an unlinked temporary file in `/var/tmp`, truncates it, and stores the file handle per connection.
- `GetSize` reads size from the temporary file metadata.
- `PRead` and `PWrite` use `ReadAt` and `WriteAt`, rejecting short I/O.
- `CanWrite` and `CanFlush` enable write and flush callbacks.
- `Flush` calls `Sync`.

Semantics:
- `CanMultiConn` returns false because each client receives a different temporary disk.
- The disk is transient and deleted after open/unlink and close.

Integration:
- Embeds `nbdkit.Plugin` and `nbdkit.Connection` defaults.
- Exports `plugin_init`, returning `nbdkit.PluginInitialize`.

Risks:
- Comments note reads/writes should loop for short I/O but currently fail instead.
- Uses deprecated `ioutil.TempFile`, reflecting older Go style.
