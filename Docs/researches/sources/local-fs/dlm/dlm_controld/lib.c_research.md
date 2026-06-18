# File Research: sources/local-fs/dlm/dlm_controld/lib.c

This file implements the user-facing `libdlmcontrol` client library for talking to `dlm_controld` over abstract AF_UNIX sockets. It wraps control and query commands into `struct dlmc_header` messages, sends them to `DLMC_SOCK_PATH` or `DLMC_QUERY_SOCK_PATH`, and decodes fixed-size or dump-style replies.

Key behavior:
- `do_read()` and `do_write()` perform full-buffer blocking I/O with EINTR retry. `do_write()` handles short writes by advancing an offset.
- `do_connect()` opens an abstract UNIX socket by writing the path into `sun_path[1]`, so no filesystem socket node is used.
- `init_header()` stamps `DLMC_MAGIC`, `DLMC_VERSION`, total length, command, optional name, flags/data/option fields as needed by each call.
- Dump APIs use `do_dump()` and a static 1 MiB `copy_buf`: `dlmc_dump_debug`, `dlmc_dump_config`, `dlmc_dump_log_plock`, `dlmc_dump_plocks`, and `dlmc_dump_run`.
- Control APIs send one-shot commands: `dlmc_reload_config`, `dlmc_set_config`, `dlmc_deadlock_check`, `dlmc_fence_ack`.
- Query APIs fetch structured data: `dlmc_lockspace_info`, `dlmc_node_info`, `dlmc_lockspaces`, `dlmc_lockspace_nodes`.
- Filesystem integration APIs keep a persistent fd: `dlmc_fs_connect`, `dlmc_fs_register`, `dlmc_fs_unregister`, `dlmc_fs_notified`, `dlmc_fs_result`.
- Cluster command execution APIs are `dlmc_run_start()` and `dlmc_run_check()`, using fixed `DLMC_RUN_COMMAND_LEN` command buffers and UUID strings returned through the header name field.
- `dlmc_print_status()` is more than a raw client call: it consumes streamed daemon state records, parses key/value strings with `kv()` and `ks()`, sorts node ids, and prints human-readable cluster/fence/startup status.

Important dependencies:
- Protocol constants and `struct dlmc_header` come from `dlm_controld.h`.
- Public structs and flags come from `libdlmcontrol.h`.
- `DLM_LOCKSPACE_LEN` comes from Linux DLM constants.
- The query/status format is tightly coupled to `main.c` query handlers and daemon state emitters elsewhere in `dlm_controld`.

Notable implementation details:
- Status parsing is simple substring/key scanning, not a structured parser.
- `dlmc_lockspace_nodes()` intentionally reads a maximum-sized reply even though the daemon may return fewer bytes; it uses `rh->data` and supports `-E2BIG`.
- `dlmc_run_check()` may reuse a single connection and retry once per second until `wait_sec` expires while status remains `DLMC_RUN_STATUS_WAITING`.
- `dlmc_set_config()` and `dlmc_run_start()` copy input into fixed 1024-byte buffers, truncating at `DLMC_RUN_COMMAND_LEN - 1`.
