# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zcp_iter.h

This header declares loading of channel-program list/iteration functions.

Core API surface:
- `zcp_load_list_funcs(lua_State *)` installs list/iterator-facing Lua functions.

Risk-sensitive invariants:
- Iterator functions expose filesystem/pool traversal to Lua and must follow channel-program limits enforced by `zcp.h`.
- The header uses the guard name `_SYS_ZCP_LIST_H`, matching the list-function naming rather than the file basename.
