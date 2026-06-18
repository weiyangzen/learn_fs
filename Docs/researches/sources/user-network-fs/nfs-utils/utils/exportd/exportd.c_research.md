<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/exportd.c -->
# sources/user-network-fs/nfs-utils/utils/exportd/exportd.c

## Purpose
`exportd` is a daemon for servicing NFSv4 export cache upcalls. It reads exportd/mountd configuration, opens kernel cache channels, optionally forks worker processes, initializes v4 client tracking, and processes export cache requests until shutdown.

## APIs And Control Flow
Important functions are `read_exportd_conf`, `set_signals`, `killer`, and `main`. Configuration populates `manage_gids`, `no_netlink`, worker thread count, state directory, cache keying mode, and TTL. Command-line options override config for foreground, debug categories, manage-gids, netlink, cache IP keying, TTL, state path, and thread count. `main` sets state path names for `etab`, daemonizes, clamps worker count to `1..64` outside foreground mode, opens cache channels before forking, delegates process fanout to `cache_fork_workers`, initializes v4 clients, and loops on `cache_process`.

## State, Dependencies, And Integration
Global state is intentionally shared with support libraries: `manage_gids`, `no_netlink`, `use_ipaddr`, `default_ttl`, and `etab` path data. It depends on support/export, support/nfs, support/misc, cache channel files, nfs.conf, daemon lifecycle helpers, and worker management functions.

## Risks And Test Signals
Risks include Linux-specific signal behavior, foreground forcing single worker, command-line/config option mismatches, and cleanup only for lock/state path names on normal signal paths. Test with foreground and daemon modes, multiple `--num-threads` values, invalid TTL, SIGHUP/SIGTERM behavior, no-netlink mode, cache upcall processing, and worker exit handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/exportd/exportd.c -->
