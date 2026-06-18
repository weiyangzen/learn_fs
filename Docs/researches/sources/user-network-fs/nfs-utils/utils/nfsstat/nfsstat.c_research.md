## sources/user-network-fs/nfs-utils/utils/nfsstat/nfsstat.c

Purpose: Implements `nfsstat`, reporting NFS client/server RPC, network, cache, filehandle, I/O, and per-procedure counters.

Important APIs/types/functions: Uses global counter arrays and `statinfo` descriptors. Main helpers include `parse_raw_statfile`, `parse_pretty_statfile`, `get_stats_netlink`, `stats_nl_handler`, `diff_stats`, `print_*` functions, and `mounts`. Option flags select client/server, versions, categories, list format, `--since`, and interval mode.

Control flow: `main` parses options, decides default client/server/category/version sets, reads current or baseline stats, optionally waits for SIGINT or loops at a sleep interval, diffs counters, and prints normal or list output. Server stats prefer generic netlink `NFSD_CMD_SERVER_STATS_GET`, falling back to `/proc/net/rpc/nfsd`; client stats use `/proc/net/rpc/nfs`.

State and persistence: Runtime state is process-local counters. Persistent inputs are `/proc/net/rpc/nfsd`, `/proc/net/rpc/nfs`, `/proc/mounts`, and optional saved pretty/raw stats file for `--since`.

Dependencies and integration: Uses libnl/genl and nfsd netlink UAPI, plus procfs formats emitted by kernel NFS client/server. Output compatibility is maintained for older kernel stat layouts.

Risks and test signals: Counter widths truncate u64 netlink counts to unsigned int in several places, proc pretty parsing is format-sensitive, interval update math is easy to regress, and server-only category warnings are non-fatal. Tests should feed fixture raw/pretty files, mocked netlink attributes, wraparound counters, mount listings, and SIGINT interval flow.
