# sources/user-network-fs/samba/source3/smbd/notifyd/notifyd.c

## Purpose
This is the core notify daemon implementation. It accepts notify interest records from smbd clients, maintains an in-memory database keyed by absolute path, registers system-level watches, dispatches trigger events to interested clients, exposes its database for introspection, and, when cluster support is compiled in, replicates notify interest between notify daemons over CTDB broadcasts.

## Important APIs, Types, and Functions
The exported tevent API is `notifyd_send()` plus `notifyd_recv()`. `struct notifyd_state` owns the event loop, messaging context, optional CTDB connection, dbwrap rbt database of entries, optional replication log, peer list, and system watch callback. `notifyd_apply_rec_change()` is the central add/update/delete path for notify instances and watcher masks. `notifyd_rec_change()` handles `MSG_SMB_NOTIFY_REC_CHANGE`; `notifyd_trigger()` and `notifyd_trigger_parser()` handle `MSG_SMB_NOTIFY_TRIGGER`; `notifyd_get_db()` marshals the local db. Cluster-only helpers include `notifyd_broadcast_reclog()`, `notifyd_got_db()`, `notifyd_apply_reclog()`, peer cleanup, and CTDB snooping.

## Control Flow
`notifyd_send()` allocates state, opens an rbt db, registers message handlers, registers the `"notify-daemon"` name exclusively, and optionally starts CTDB replication timers and srvid registration. On a record-change message, `notifyd_rec_change()` validates the variable-length payload, copies the possibly unaligned `notify_instance`, and calls `notifyd_apply_rec_change()`. That function locks the path record, parses existing watcher/instances, updates or appends the client instance, recalculates aggregate filters on delete or expansion, refreshes the system watch when masks change, and either deletes or stores the record. On a trigger, `notifyd_trigger()` walks each ancestor path component and parses local plus peer records. `notifyd_trigger_parser()` computes whether direct or recursive filters match, sends `MSG_PVFS_NOTIFY` with the path relative to the watched directory, and schedules deletion of dead local clients.

## State and Persistence
The entries database is in-memory `db_open_rbt()` state, not a durable TDB. Record keys are absolute paths without trailing nul. Values are raw `struct notifyd_watcher` followed by an array of `struct notifyd_instance`, parsed by `notifyd_parse_entry()`. `watcher.sys_watch` is a live talloc handle and is stored inside the raw value, so db values are process-local and only meaningful inside the daemon. Cluster peer dbs are unmarshalled snapshots plus replayed reclogs and are discarded when stale or out of sequence.

## Dependencies and Integration Points
The daemon depends on Samba messaging, dbwrap rbt, tevent, server-id names, generated NDR messaging structs, CTDB APIs under `CLUSTER_SUPPORT`, and the pluggable `sys_notify_watch_fn` provided by inotify or a dummy. It integrates upward with smbd through `notify_msg.c` and downward with `notify_inotify.c`. `notifyd_db.c` queries its db through `MSG_SMB_NOTIFY_GET_DB`.

## Risks and Edge Cases
The raw db value embeds pointers and native structs, so alignment, same-process lifetime, and architecture consistency matter. `notifyd_apply_rec_change()` logs `strerror(errno)` for system-watch failure even though the callback returns an integer `ret`, which can misreport errors. Trigger path walking only considers paths beginning with `/` and only components before slashes; malformed paths are ignored. Replication assumes ordered broadcasts and drops a peer on rec_index mismatch, trading correctness for resynchronization. Dead-client cleanup sends a delete message to `instance->client`; if that process is gone, delivery semantics deserve scrutiny because the comment says it sends to itself.

## Test Signals
`test_notifyd_trigger1` covers basic registration and trigger delivery for `/home` to `/home/foo`. `test_notifyd_dbtest1` covers add/remove visibility through `notify_walk()`. `tests.c` stress-sends 50,000 add/delete records and then pings notifyd. Cluster replication, system watch refresh, dead-client cleanup, ancestor walking, and recursive filter masking are not deeply covered in this group.
