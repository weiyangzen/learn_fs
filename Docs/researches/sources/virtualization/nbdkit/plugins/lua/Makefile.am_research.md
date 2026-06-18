# File Research: sources/virtualization/nbdkit/plugins/lua/Makefile.am

This Automake file builds the Lua language plugin when Lua is available.

Key behavior:
- Distributes the POD and `example.lua`.
- Gated by `HAVE_LUA`.
- Builds `nbdkit-lua-plugin.la` from `lua.c`.
- Uses Lua compiler/linker flags.
- Uses module/shared flags and optional linker version script.
- Builds `nbdkit-lua-plugin.3` when POD tooling is available.

Integration:
- The Lua plugin is a language binding plugin rather than a direct storage backend.
