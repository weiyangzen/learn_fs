# File Research: sources/os/linux/linux-stable/fs/dlm/lowcomms.h

## Purpose
`lowcomms.h` declares the DLM low-level socket transport API used primarily by `midcomms.c`, recovery, membership, and memory-cache setup.

## Exports
- Lifecycle: `dlm_lowcomms_start()`, `dlm_lowcomms_shutdown()`, `dlm_lowcomms_stop()`, `dlm_lowcomms_init()`, `dlm_lowcomms_exit()`.
- Node/socket control: `dlm_lowcomms_close()`, `dlm_lowcomms_connect_node()`, `dlm_lowcomms_nodes_set_mark()`, `dlm_lowcomms_addr()`.
- Message API: `dlm_lowcomms_new_msg()`, `dlm_lowcomms_commit_msg()`, `dlm_lowcomms_put_msg()`, `dlm_lowcomms_resend_msg()`.
- Cache factories: `dlm_lowcomms_writequeue_cache_create()`, `dlm_lowcomms_msg_cache_create()`.

## Definitions
- `DLM_MIDCOMMS_OPT_LEN` reserves space for `struct dlm_opts`.
- `DLM_MAX_APP_BUFSIZE` subtracts midcomms option overhead from socket-buffer capacity.
- `CONN_HASH_SIZE` is 32.
- `nodeid_hash()` maps node ids with `nodeid & (CONN_HASH_SIZE - 1)`.

## Notes
The header also declares `dlm_lowcomms_shutdown_node()` and `dlm_midcomms_receive_done()`, but these declarations have no matching definitions in this source tree. They appear to be stale API leftovers.
