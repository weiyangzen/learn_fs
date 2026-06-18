# File Research: sources/os/linux/linux/fs/dlm/dlm_internal.h

## Role

`dlm_internal.h` is the central private DLM header. It defines core lockspace, resource, lock, message, recovery, callback, and userspace-process structures shared by the implementation files in `fs/dlm`.

## Logging and Assertion Support

The header defines DLM-specific logging macros:

- `log_print()` and `log_print_ratelimited()` for global DLM errors.
- `log_error(ls, ...)` for lockspace-tagged errors.
- `log_rinfo()`, `log_debug()`, and `log_limit()` gated by `dlm_config`.

`DLM_ASSERT()` logs file, line, assertion text, and time, executes a caller-provided diagnostic block, then panics. This is used in lock/resource state invariants where continuing could corrupt distributed lock state.

## Core Membership and Recovery Types

`struct dlm_member` records a member nodeid, weight, slot, previous slot, comm sequence, and generation.

`struct dlm_recover` packages recovery arguments: a node list, node count, and recovery sequence.

Recovery status flags (`DLM_RS_*`) track progress through node, directory, locks, and completion phases. `struct dlm_ls` stores the current recovery sequence, request queue, recovery buffers, recovered resources, removed nodes, and wait queues used by recovery code.

## Lock Blocks

`struct dlm_lkb` is the lock block. It contains:

- Resource pointer and `kref`.
- Local and remote lock ids.
- Master/process nodeid interpretation.
- External DLM flags, internal flags, distributed flags, status-block flags, and LVB sequence.
- Queue status: waiting, granted, or converting.
- Granted and requested modes.
- Waiter state for outstanding remote replies.
- Links for RSB queues, lookup waits, reply waiters, and per-process ownership.
- Callback state, timestamps, LVB pointer, lksb pointer, and either kernel AST parameter or userspace args.

The comments explain the three LKB forms:

- Local copy: lock is mastered locally.
- Process copy: local representation of a lock mastered remotely.
- Master copy: master node's representation of a remote holder's lock.

Internal flags are bit-indexed (`DLM_IFL_*_BIT`) and split conceptually between shared lower bits and private high bits. Distributed flags include `DLM_DFL_USER_BIT` and `DLM_DFL_ORPHAN_BIT`.

## Resource Blocks

`struct dlm_rsb` is the resource block. It contains:

- Lockspace pointer and `kref`.
- `res_lock` spinlock.
- Resource name, length, hash, and directory/master node ids.
- The legacy `res_nodeid` field, where `-1` means unknown, `0` means local master, and positive values mean remote master.
- Grant, convert, wait, and lookup queues.
- Slow active/inactive list linkage.
- Scan, root, masters, and recovery list linkage.
- Recovery lock count, LVB pointer/sequence, toss time, and flags.

RSB flags include master uncertainty, LVB validity, recovery conversion/grant/invalidation markers, inactive state, and rhashtable membership.

## Wire Protocol Structures

The header defines the DLM wire protocol layout:

- `struct dlm_header`, common to all inter-node packets.
- `struct dlm_message`, used for normal locking messages such as request, convert, unlock, cancel, grant, BAST, lookup, remove, and purge.
- `struct dlm_rcom`, used for recovery communication.
- `struct dlm_opts` and option headers.
- `union dlm_packet`, the dispatch overlay used by receive paths.

It also defines protocol constants such as `DLM_HEADER_MAJOR`, `DLM_HEADER_MINOR`, `DLM_VERSION_3_1`, `DLM_VERSION_3_2`, command ids, message type ids, recovery-communication type ids, and RCOM payload structures.

## Lockspace Structure

`struct dlm_ls` is the top-level lockspace object. Important groups of fields:

- Identity and lifetime: global id, generation, flags, refcounts, kobject, miscdevice, and name.
- Lock/resource indexes: `ls_lkbxa`, `ls_rsbtbl`, slow active/inactive lists, scan timer/list.
- Reply waiters and orphan locks.
- Current and gone member lists, node arrays, slots, weights.
- Debugfs dentries.
- User-control wait queue and recovery completion.
- Callback worker state.
- Recovery synchronization: `ls_in_recovery`, `ls_recv_active`, requestqueue, rcom sequence, recover lists, recovery xarray, master list, directory dump contexts.
- Optional filesystem/user callbacks.

The final member is `ls_local_ms`, a flexible-array-adjacent local message object used to synthesize replies.

## Inline Helpers

The header provides helpers for:

- Testing lockspace state: `dlm_locking_stopped()`, `dlm_recovery_stopped()`, `dlm_no_directory()`.
- Setting/testing RSB flags.
- Snapshotting and restoring bitfield ranges into wire-visible integer flag values: `dlm_iflags_val()`, `dlm_dflags_val()`, `dlm_sbflags_val()`, `dlm_set_dflags_val()`, `dlm_set_sbflags_val()`.

The status-block flag helper has a `BUILD_BUG_ON()` to ensure the bit mapping matches UAPI constants.

## Userspace DLM State

`struct dlm_user_args` stores userspace lock metadata, user pointers, an in-kernel lksb copy, and transaction id.

`struct dlm_user_proc` tracks a process's lockspace device handle, pending AST callbacks, held locks, in-progress unlocks, and wait queue. This is the bridge between kernel DLM state and `/dev/misc` DLM user APIs.

## Debugfs Conditional Boundary

When `CONFIG_DLM_DEBUG` is enabled, the header declares debugfs creation/removal and per-node comms debug functions. When disabled, the same functions are inline no-ops, keeping call sites simple.

## Research Notes

This header is the DLM subsystem's internal contract. The most important invariants for readers are the dual nodeid model in `struct dlm_rsb`, the three LKB copy types, queue ownership under `res_lock`, lockspace-wide indexes under `ls_lkbxa_lock`/`ls_rsbtbl_lock`, and the recovery gating represented by `ls_in_recovery` plus `LSFL_RUNNING`/`LSFL_RECOVER_*`.
