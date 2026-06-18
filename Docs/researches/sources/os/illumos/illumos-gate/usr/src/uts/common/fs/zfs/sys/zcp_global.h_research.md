# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_global.h

This header declares loading of global symbols into a ZFS channel-program Lua state.

Core API surface:
- `zcp_load_globals(lua_State *)` installs supported globals.

Risk-sensitive invariants:
- The function mutates the Lua environment used by channel programs.
- Exported globals are part of the scripting compatibility and safety surface.
