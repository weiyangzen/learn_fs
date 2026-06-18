# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.c

Purpose: implements a `dbwrap` decorator that stores watcher metadata before record payloads and wakes waiting Samba processes via messaging when a watched record changes.

Important APIs/types/functions: `struct dbwrap_watcher`, `struct db_watched_record`, `db_open_watched()`, watcher instance add/remove helpers, alert-control helpers, `dbwrap_watched_watch_send()/recv()`, `dbwrap_watch_rec_parse()`, and `dbwrap_watched_record_storev()`.

Control flow: fetch/do-locked paths parse the watcher header, expose only user data, and replace store/delete with wrapper methods. Mutations select the first live watcher, persist the rebuilt watcher header plus payload, and later send `MSG_DBWRAP_MODIFIED`. Watch requests add or resume an instance, wait through `messaging_filtered_read_send()`, and can also watch blocker death.

State/persistence behavior: each record is encoded as watcher count, fixed-size watcher array, then user payload. Empty records are fresh records. Watcher add/remove is persisted at store or destructor time, and invalid headers are logged and treated as empty payload.

Dependencies/integration: depends on dbwrap, messaging, server-id helpers, `server_id_watch`, TDB utilities, NTSTATUS, and tevent. `g_lock.c` is a major consumer; torture tests cover dbwrap watch/do-locked behavior.

Risks/test signals: risks are stale watcher instances, corrupt headers hiding payload, missed destructor cleanup, and fairness around first-watcher wakeups. Tests should cover add/remove, instance resumption, blocker death, invalid records, and avoiding alerts for metadata-only changes.
