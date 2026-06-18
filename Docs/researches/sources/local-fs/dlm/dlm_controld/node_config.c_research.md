# File Research: sources/local-fs/dlm/dlm_controld/node_config.c

This file parses optional per-node DLM configuration from a text file, currently only `mark` values.

Key behavior:
- Static `nc[MAX_NODES]` stores per-node `struct node_config`.
- `nc_default` has `.mark = 0`.
- `node_config_init(path)` opens the config file; if missing, it logs and uses default zero marks.
- It skips comments and blank lines.
- It parses lines of the form `node id=<nodeid> mark=<value>`.
- Invalid line syntax returns `-EINVAL`; invalid node ids are skipped.
- `node_config_get(nodeid)` returns `nc_default` for out-of-range ids, otherwise the array entry.

Important dependencies:
- Included through `dlm_daemon.h`, with `MAX_NODES`, logging, and integer format macros.
- Consumed by `member.c` when creating configfs comms nodes.

Notable details:
- Static storage starts zeroed, so unconfigured in-range nodes effectively get mark 0.
- `strtoul()` is used with base 0 for decimal/hex-style input.
- The overflow/error check compares to `ULONG_MAX` but does not inspect `errno`.
