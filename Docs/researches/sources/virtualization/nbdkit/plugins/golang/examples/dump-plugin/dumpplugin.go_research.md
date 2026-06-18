# File Research: sources/virtualization/nbdkit/plugins/golang/examples/dump-plugin/dumpplugin.go

This Go example is a minimal read-only zero disk that also demonstrates `DumpPlugin`.

Key behavior:
- `DumpPlugin` prints `golang_dump_plugin=1`.
- `Open` returns a stateless connection.
- `GetSize` returns a fixed 1 MiB size.
- `PRead` fills the buffer with zeroes.

Integration:
- Uses required cgo boilerplate: imports `C` and `unsafe`, exports `plugin_init`, and calls `nbdkit.PluginInitialize`.
- Used by the build test to verify `--dump-plugin` behavior.
