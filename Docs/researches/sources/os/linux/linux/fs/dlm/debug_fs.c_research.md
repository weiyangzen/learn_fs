# File Research: sources/os/linux/linux/fs/dlm/debug_fs.c

## Role

`debug_fs.c` implements DLM debugfs surfaces under `/sys/kernel/debug/dlm`. It exposes per-lockspace lock/resource snapshots, waiter lists, inactive/tossed resource records, and midcomms per-node state. It is compiled behind `CONFIG_DLM_DEBUG`; `dlm_internal.h` provides no-op inline stubs when debug support is disabled.

## Main Interfaces

- `dlm_register_debugfs()` initializes `debug_buf_lock` and creates the top-level `dlm` and `dlm/comms` debugfs directories.
- `dlm_unregister_debugfs()` removes the top-level tree.
- `dlm_create_debug_file(struct dlm_ls *ls)` creates per-lockspace files:
  - `<ls_name>`: human-readable resource/lock dump using format 1.
  - `<ls_name>_locks`: compact lock table using format 2; writable for debug lock injection.
  - `<ls_name>_all`: resource plus all lock queues using format 3.
  - `<ls_name>_toss`: inactive resource/toss-list view using format 4.
  - `<ls_name>_waiters`: waiters-list view; writable for debug waiter injection.
- `dlm_delete_debug_file(struct dlm_ls *ls)` removes all per-lockspace debugfs dentries stored in `struct dlm_ls`.
- `dlm_create_debug_comms_file(int nodeid, void *data)` creates `dlm/comms/<nodeid>/` files for midcomms state, flags, send queue count, protocol version, and raw message injection.
- `dlm_delete_debug_comms_file(void *ctx)` removes a per-node comms directory.

## Resource Dump Formats

The file implements four seq_file formats over the lockspace slow resource lists:

- Format 1 (`print_format1`) is a readable dump of one active resource at a time. It prints the resource address, name, master state, optional LVB contents, recovery-list membership, and the granted/convert/waiting/lookup queues.
- Format 2 (`print_format2`) emits a machine-readable row per active lock with fields such as local id, remote node/id, owner pid, user xid, external flags, internal flags, status, granted/requested modes, queue age, resource nodeid, name length, and name.
- Format 3 (`print_format3`) emits detailed active RSB records, optional LVB bytes, and LKB rows including callback history and timestamps. It prints resource names as text only if fully printable ASCII, otherwise as hex bytes.
- Format 4 (`print_format4`) walks `ls_slow_inactive` instead of `ls_slow_active` and emits inactive/tossed resource records with current node, master node, directory node, local node, toss time, flags, and name.

The shared `table_seq_*` implementation selects `ls_slow_active` for formats 1-3 and `ls_slow_inactive` for format 4. It holds `ls_rsbtbl_lock` in read mode while iterating the list and then locks each RSB with `lock_rsb()` while formatting detailed resource contents.

## Debug Mutation Paths

Two debugfs write paths are intentionally invasive:

- Writing to `<ls_name>_locks` parses `lkb_id name lkb_flags lkb_nodeid lkb_status` and calls `dlm_debug_add_lkb()`.
- Writing to `<ls_name>_waiters` parses `lkb_id mstype to_nodeid`, takes the recovery read lock with `dlm_lock_recovery_try()`, then calls `dlm_debug_add_lkb_to_waiters()`.

Both paths copy user input into bounded stack buffers, use `sscanf`, and return `-EINVAL` for malformed input. They are debug-only hooks into the live lock manager and therefore rely on the locking/recovery contracts implemented in `lock.c`.

## Waiters and Shared Buffer Handling

`waiters_read()` uses a single global 4096-byte `debug_buf` protected by `debug_buf_lock`. It refuses to run if it cannot take a recovery read lock, returning `-EAGAIN`. While holding `ls_waiters_lock`, it prints waiter LKB id, wait type, nodeid, and resource name until the fixed buffer fills.

This design avoids per-read allocation, but it also means the output is truncated silently at the global buffer size. That is acceptable for debugfs but important for tooling that expects complete waiter coverage.

## Midcomms Debugfs

The per-node `comms` directory exposes:

- `state`: `dlm_midcomms_state(data)`
- `flags`: `dlm_midcomms_flags(data)`
- `send_queue_count`: `dlm_midcomms_send_queue_cnt(data)`
- `version`: `dlm_midcomms_version(data)`
- `rawmsg`: write-only raw DLM packet injection through `dlm_midcomms_rawmsg_send()`

`rawmsg` requires `count` between `sizeof(struct dlm_header)` and `PAGE_SIZE`, allocates one page with `GFP_NOFS`, copies from userspace, and delegates validation/sending to midcomms.

## Dependencies

This file depends on:

- `dlm_internal.h` for core DLM structures and debugfs declarations.
- `lock.h` for `lock_rsb()`, waiter/recovery helpers, and debug injection helpers.
- `ast.h` indirectly for callback-facing lock information.
- `midcomms.h` for comms status and raw message send support.
- Linux `seq_file`, `debugfs`, and user-copy APIs.

## Concurrency Notes

- RSB contents are printed under `res_lock`.
- Slow-list iteration is protected by `ls_rsbtbl_lock`.
- Waiters output is protected by both `debug_buf_lock` and `ls_waiters_lock`, and gated by the recovery rwsem.
- The file assumes debugfs files are removed during lockspace teardown before the underlying `struct dlm_ls` is finally freed.

## Research Notes

`debug_fs.c` is observability-first but not read-only: it includes synthetic LKB and waiter insertion hooks used for testing/recovery debugging. The most important downstream readers are DLM operators and test harnesses trying to understand live queue state, recovery state, and midcomms behavior.
