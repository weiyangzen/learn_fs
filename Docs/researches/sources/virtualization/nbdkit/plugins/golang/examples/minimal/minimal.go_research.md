# File Research: sources/virtualization/nbdkit/plugins/golang/examples/minimal/minimal.go

This is the smallest practical Go nbdkit plugin example.

Behavior:
- Opens a stateless connection.
- Reports a fixed 1 MiB export.
- Reads return zero-filled data.
- Does not implement writes, flush, trim, zero, or config.

Integration:
- Demonstrates the required Go plugin boilerplate: `C` import, `unsafe`, exported `plugin_init`, and a dummy `main`.
- Embeds default `nbdkit.Plugin` and `nbdkit.Connection` implementations.
