<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfs-iostat/nfs-iostat.py -->
# sources/user-network-fs/nfs-utils/tools/nfs-iostat/nfs-iostat.py

## Purpose

`nfs-iostat.py` is an iostat-like NFS client reporting tool. It reads `/proc/self/mountstats`, isolates NFS and NFSv4 mount entries, parses per-mount VFS, byte, transport, and per-RPC-operation counters, and prints interval or since-mount summaries for file I/O, attribute cache, directory cache, or page cache activity.

## Important APIs, Types, and Functions

`DeviceData` owns parsed NFS and RPC dictionaries for one mount. `__parse_nfs_line` handles mount identity, age, options, capabilities, security, event counters, and byte counters; `__parse_rpc_line` handles RPC header, transport statistics for `udp`, `tcp`, and `rdma`, and per-op rows. `compare_iostats` computes deltas against an older snapshot. `display_iostats`, `__print_rpc_op_stats`, and cache/page helper printers format reports. `parse_stats_file`, `list_nfs_mounts`, `print_iostat_summary`, and `iostat_command` are the command-level parsing and reporting pipeline.

## Control Flow

Startup parses the current mountstats file, interprets positional arguments as mountpoints, interval, and count, and configures display mode through `optparse`. The first report shows counters since mount age. If an interval is provided, the loop sleeps, reparses mountstats, filters current NFS mounts again to handle mount churn, computes deltas against the previous snapshot, optionally sorts by operations per second, and prints up to `--list` entries.

## State and Persistence Behavior

The script keeps only in-memory snapshots. It does not persist state or modify the system. The durable source of truth is the kernel-generated `/proc/self/mountstats`; interval reports are derived by subtracting previous in-process counters.

## Dependencies and Integration Points

It depends on Python 3 standard modules, `/proc/self/mountstats` format, NFS client stat versions, and shell invocation as the installed `nfsiostat` tool. It integrates with nfs-utils packaging and user diagnostics rather than daemon control paths.

## Risks and Edge Cases

Parsing is tightly coupled to mountstats field positions, including older non-`device` lines and `statvers` handling. `parse_stats_file` misses `f.close()` parentheses, relying on process cleanup. Several cache views assume operations such as `LOOKUP`, `READDIR`, `READ`, or `WRITE` exist in parsed RPC data. Counter wrap, remounts, transport field changes, or malformed proc data can produce bad deltas or `KeyError`s. The argument parser treats an argument as a mountpoint only if its normalized path exists in the initial snapshot, so newly mounted paths cannot be selected later in the same run.

## Test Signals

Useful tests should feed fixture mountstats data for NFSv3, NFSv4, TCP, UDP, and RDMA; verify first-sample and delta math; cover zero-age and zero-operation divisions; check sort/list behavior; test mount disappearance; and exercise each display mode against missing optional ops such as `READDIRPLUS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfs-iostat/nfs-iostat.py -->
