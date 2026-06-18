# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_client_debug.c

## Purpose
NFSv4 client recovery diagnostics and kstats. This file builds and manages per-mount recovery event/fact queues, formats user-visible diagnostic messages, deduplicates recent messages, and updates per-mount recovery counters.

## Main Data
- `rkstat_t`: named kstat counters for recovery conditions such as `badhandle`, `badowner`, `clientid`, `dead_file`, `delay`, `fail_relock`, `opens_changed`, `wrongsec`, and `lost_state_bad_op`.
- `rkstat_template`: initialization template for `mi_recov_kstat`.
- `nfs4_msg_max`: maximum queued recovery messages per mount.

## Event And Fact Construction
`set_event()` fills an `nfs4_revent_t` according to `nfs4_event_type_t`. It records affected rnodes, paths from `fn_path()`, pids, seqids, NFS status values, server names, and explanatory strings. It handles events such as:
- bad seqid
- bad filehandle
- clientid recovery failure
- dead file
- recovery start/end
- failed relock
- failover/referral
- lost state
- changed open counts
- lost locks
- unexpected recovery action/error/status
- wrong security

`set_fact()` fills `nfs4_rfact_t` entries for contextual facts including bad owner/domain mismatch, recovery error causes, renew expiration, server response transitions, delmap callback errors, and full send queues.

## Queue Interpretation
`successful_comm()` classifies whether a message represents successful server communication. `find_beginning()` walks backward through the mount message list to find the earliest relevant message for a fact sheet, bounded by roughly two lease periods or a default lease window. It includes logic to identify where communication was lost before recovery.

`get_facts()` walks backward from an event to collect not-yet-inspected facts into a summarized fact sheet, marking facts as inspected so repeated severe events do not repeatedly reuse the same historical context.

## Deduplication
`facts_same()` compares a new fact with recent facts within two lease periods. It compares type, recovery action, NFS status, reboot flag, op, time, errno, rnode pointer, server, mount point, and path strings.

`events_same()` compares a new event against the most recent prior event, skipping facts. It compares event type, mount, counters, status, pid, rnodes, tags, seqids, server, path strings, and mount point. This prevents repeated identical recovery noise from filling the queue or logs.

## Memory Management
- `free_event()` frees event path/string fields.
- `free_fact()` frees fact string fields.
- `nfs4_free_msg()` frees event/fact payload strings, server/mount strings, and the message itself.

## Logging
`queue_print_event()` formats recovery events into zone-aware `zcmn_err()` messages. It prints detailed messages for bad seqids, invalid filehandles, failed clientid recovery, dead files, failover, remap failures, lost state, failed relock, lost locks, unexpected recovery outputs, unrecoverable `WRONGSEC`, bad lost-state ops, and referrals. It calls `print_facts()` for severe file/lock-loss events.

`queue_print_fact()` formats standalone facts such as:
- `NFSMAPID_DOMAIN` mismatch
- operation error causing recovery action
- lease expiration
- server not responding/ok
- all servers not responding/ok
- delmap callback error
- send queue full

`id_to_dump_queue()`, `id_to_dump_solo_event()`, and `id_to_dump_solo_fact()` control whether a new message dumps the whole queue, only itself, or stays queued silently.

## Kstats
`update_recov_kstats()` increments recovery kstat counters from events and facts. `nfs4_mnt_recov_kstat_init()` creates the per-mount named kstat under module `nfs`, installs the `rkstat_template`, handles zone visibility, and stores the kstat pointer on `mntinfo4_t`.

Small helpers:
- `nfs4_mi_kstat_inc_delay()`
- `nfs4_mi_kstat_inc_no_grace()`

## Public Queue APIs
`nfs4_queue_event()` allocates and initializes an event message, records server and mount path, deduplicates it against the last event, inserts it at the tail, dumps/logs as dictated by the event type, and trims the queue when `nfs4_msg_max` is reached.

`nfs4_queue_fact()` performs the analogous path for facts. It updates kstats, deduplicates recent facts, queues the fact, optionally prints standalone facts, and trims the queue.

## Notable Detail
In `events_same()`, the mount-point string comparison uses `strncmp(cur_msg->msg_mntpt, cur_msg->msg_mntpt, len)`, comparing the string to itself rather than `new_msg->msg_mntpt`. That makes the mount-point content check ineffective once both are non-NULL; other fields still participate in deduplication.
