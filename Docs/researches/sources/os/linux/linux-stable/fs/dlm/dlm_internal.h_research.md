# File Research: sources/os/linux/linux-stable/fs/dlm/dlm_internal.h

## Purpose
`dlm_internal.h` is the main private DLM header. It defines core in-kernel structures, message formats, state flags, logging helpers, and inline flag conversion helpers used across the DLM implementation.

## Core Structures
- `struct dlm_member`: one lockspace member, with node id, weight, slot, comm sequence, and generation.
- `struct dlm_recover`: recovery input containing member configuration and sequence.
- `struct dlm_args`: internal normalized arguments for lock/unlock operations.
- `struct dlm_user_args`: userspace lock metadata and user pointers copied back through callbacks.
- `struct dlm_callback`: queued AST/BAST callback record.
- `struct dlm_lkb`: lock block. Tracks resource pointer, refcount, ids, remote ids, external/internal/status flags, status queue membership, waiters state, callback state, LVB pointer, and user/kernel callback parameters.
- `struct dlm_rsb`: resource block. Tracks lockspace, refcount, resource name, hash, master/directory node ids, LVB state, grant/convert/wait queues, lookup queue, slow active/inactive list linkage, scan/recovery/master lists, and recovery flags.
- `struct dlm_ls`: lockspace state. Holds global id, refcounts, flags, RSB hash table, LKB xarray, waiters/orphans, members, debugfs dentries, recovery state, request queue, masters/directory-dump lists, scan timer/list, callbacks, user device, and lockspace name.

## Protocol Types
Defines the common `struct dlm_header`, normal `struct dlm_message`, recovery `struct dlm_rcom`, options structures, and `union dlm_packet`.

Message types include request, convert, unlock, cancel, replies, grant, BAST, lookup, remove, and purge. RCOM types cover recovery status, names, lookup, lock transfer, and replies. Recovery status bits track nodes, directory, locks, and done phases.

## Flags and Inline Helpers
Defines:
- LKB status values: waiting, granted, convert.
- Internal LKB flag bit ranges (`DLM_IFL_*`) and distributed flag bits (`DLM_DFL_*`).
- RSB flags for master uncertainty, LVB validity, new master, recovery convert/grant/LVB invalidation, inactive, and hashed.
- Lockspace flags (`LSFL_*`) for recovery control, running state, no-directory mode, softirq behavior, receive blocking, and filesystem users.

Inline helpers include:
- `rsb_set_flag()`, `rsb_clear_flag()`, `rsb_flag()`.
- `dlm_locking_stopped()`, `dlm_recovery_stopped()`, `dlm_no_directory()`.
- Bitfield snapshot/set helpers for internal, distributed, and status-block flags.

## Debug Configuration
Under `CONFIG_DLM_DEBUG`, declares debugfs registration and per-lockspace/per-comms debug file helpers. Otherwise, it provides no-op stubs.

## Integration
This header ties together nearly every file in `fs/dlm`. `lock.c` is its heaviest consumer, using LKB/RSB/lockspace layouts and protocol structs. `lockspace.c` owns creation/destruction of `struct dlm_ls`, and `debug_fs.c` reads many fields directly.

## Risks and Notes
The header encodes wire-visible structures and private in-memory state in one place. Changing fields, bit ranges, or endian-marked protocol structs has broad compatibility implications. Comments call out historical quirks, especially the difference between `res_master_nodeid` and `res_nodeid`.
