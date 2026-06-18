# File Research: sources/os/linux/linux-stable/fs/dlm/debug_fs.c

## Purpose
`debug_fs.c` implements DLM debugfs visibility and limited debug mutation hooks. It creates `/sys/kernel/debug/dlm` files per lockspace for RSB/LKB state dumps, waiters inspection, and communication-peer state under `dlm/comms`.

## Main Interfaces
- `dlm_register_debugfs()` / `dlm_unregister_debugfs()` create and remove the top-level debugfs directories.
- `dlm_create_debug_file()` / `dlm_delete_debug_file()` create per-lockspace files:
  - `<ls_name>`: human-readable RSB dump.
  - `<ls_name>_locks`: compact lock table, writable for debug LKB injection.
  - `<ls_name>_all`: detailed RSB/LKB dump.
  - `<ls_name>_toss`: inactive/tossed RSB dump.
  - `<ls_name>_waiters`: waiters list, writable for debug waiter injection.
- `dlm_create_debug_comms_file()` / `dlm_delete_debug_comms_file()` expose per-node midcomms state, flags, queue count, protocol version, and `rawmsg`.

## Behavior
The file defines four seq-file formats over lockspace RSB lists:
- Format 1 is readable narrative output: resource name, master state, LVB bytes, recovery flags, and granted/convert/wait/lookup queues.
- Format 2 is a one-line-per-lock table with ids, node ids, flags, status, modes, queue time, and resource name.
- Format 3 emits detailed RSB records, LVB records, and LKB records, including callback timing and lookup entries.
- Format 4 dumps inactive/toss-list RSBs, including current node, master node, directory node, toss time, flags, and printable/hex resource names.

The seq iterator takes `ls_rsbtbl_lock` in read mode while walking `ls_slow_active` or `ls_slow_inactive`, and each printer also takes the individual RSB spinlock while reading queues. Overflow checks stop expensive formatting once the seq buffer is full.

## Debug Mutation Hooks
`table_write2()` parses `lkb_id name flags nodeid status` and calls `dlm_debug_add_lkb()`. `waiters_write()` parses `lkb_id mstype to_nodeid` and calls `dlm_debug_add_lkb_to_waiters()`. Both are debug-only paths that intentionally alter internal lock state for testing.

`waiters_read()` uses `debug_buf_lock`, attempts `dlm_lock_recovery_try()`, then dumps `ls_waiters` under `ls_waiters_lock`. If recovery lock acquisition fails, it returns `-EAGAIN`.

## Midcomms Debug Hooks
The `comms/<nodeid>/` files read state from `midcomms` helper functions. `rawmsg` copies a user buffer up to `PAGE_SIZE` and sends it through `dlm_midcomms_rawmsg_send()`.

## Dependencies
Depends on `dlm_internal.h` structures, `lock.h` lock/recovery/debug helpers, `ast.h`, and `midcomms.h`.

## Risks and Notes
The writable debugfs files are powerful: they can inject LKBs, waiters, and raw DLM messages. The code relies on debugfs permissions and `CONFIG_DLM_DEBUG`. Output formatting prints resource names with `%s` in some formats even though DLM names are length-tracked; the file generally limits names through fixed buffers and DLM maximum length.
