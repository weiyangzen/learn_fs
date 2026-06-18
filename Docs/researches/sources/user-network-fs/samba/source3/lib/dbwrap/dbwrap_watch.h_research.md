# sources/user-network-fs/samba/source3/lib/dbwrap/dbwrap_watch.h

Purpose: declares the watched-dbwrap API for code that needs asynchronous notification when a locked database record changes.

Important APIs/types/functions: `db_open_watched()`, `dbwrap_watched_watch_add_instance()`, `dbwrap_watched_watch_remove_instance()`, alert controls, and `dbwrap_watched_watch_send()/recv()`.

Control flow: callers wrap a backend DB, operate on locked watched records, register or resume watcher instances, then wait asynchronously for modification or blocker death.

State/persistence behavior: watcher state is associated with locked `db_record` lifetimes and persisted by the implementation into the record header.

Dependencies/integration: includes tevent, dbwrap, and messaging types. Used by `g_lock.c` and watch torture tests.

Risks/test signals: callers must use records from a watched DB only. Tests should validate unsupported messaging contexts, instance keep/remove behavior, and wakeup delivery.
