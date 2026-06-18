# File Research: sources/virtualization/nbdkit/plugins/lua/example.lua

This Lua script is an example plugin that serves a local file.

Key behavior:
- `dump_plugin` prints `example_lua=1`.
- `config` accepts `file=<path>` and rejects unknown parameters.
- `config_complete` requires `file`.
- `open` opens the file in `rb` or `r+b` depending on readonly mode and returns the Lua file handle.
- `close` closes the handle.
- `get_size` seeks to end and returns file size.
- `pread` seeks and reads the requested bytes.
- `pwrite` seeks and writes the supplied buffer.

Integration:
- Intended to be run through `nbdkit lua example.lua file=disk.img`.
- Demonstrates that Lua handles can be arbitrary Lua objects.
