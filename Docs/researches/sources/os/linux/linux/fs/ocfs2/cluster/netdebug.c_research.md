# File Research: sources/os/linux/linux/fs/ocfs2/cluster/netdebug.c

Debugfs support for O2Net, compiled only with `CONFIG_DEBUG_FS`.

Debugfs files:
- `o2net/send_tracking`: active message-send tracking records.
- `o2net/sock_containers`: detailed socket container state.
- `o2net/stats`: compact CSV-like socket statistics for tooling.
- `o2net/connected_nodes`: bitmap-style list of connected node numbers.

Tracking lists:
- Maintains `sock_containers` and `send_tracking` under `o2net_debug_lock`.
- `o2net_debug_add_nst()` / `del_nst()` add and remove send tracking records.
- `o2net_debug_add_sc()` / `del_sc()` add and remove socket containers.

Seq-file implementation:
- Uses dummy tracking/container records inserted into the lists to support iteration while real objects may be added/removed.
- Show functions take the debug lock while reading object fields.
- Socket details include refs, IPv4 endpoints, remote node name, page offset, handshake state, timing fields, current message key/type.
- Stats output version is `O2NET_STATS_STR_VERSION == 1`.

Init/exit:
- `o2net_debugfs_init()` creates the directory and files.
- `o2net_debugfs_exit()` removes the subtree.

Dependency:
- Reads internals from `tcp_internal.h`, so this is tightly coupled to O2Net transport structures.
