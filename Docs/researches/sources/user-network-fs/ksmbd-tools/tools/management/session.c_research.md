# sources/user-network-fs/ksmbd-tools/tools/management/session.c

## Purpose

`session.c` manages ksmbd userspace session objects and their tree connections. It keeps a hash table keyed by session ID, reference-counts sessions, binds tree connections to sessions, and enforces the configured maximum active session capacity. The source was read as a complete 217-line file.

## Important APIs, Types, and Functions

Public functions are `sm_init`, `sm_destroy`, `sm_handle_tree_connect`, `sm_handle_tree_disconnect`, and `sm_check_sessions_capacity`. Important internals include `new_ksmbd_session`, `kill_ksmbd_session`, `sm_lookup_session`, `__get_session`, `__put_session`, and `__sm_remove_session`. State is `sessions_table`, `sessions_table_lock`, each session's `update_lock`, `ref_counter`, `id`, `user`, and `tree_conns`.

## Control Flow

Tree connect first checks capacity; if no session exists, it allocates one, takes the table writer lock, handles a concurrent insertion race, and inserts the session. The tree connection is appended under the session update lock. Tree disconnect looks up the session, increments global capacity, finds the matching connection, removes it, decrements the session refcount, frees the tree connection, and puts the session reference.

## State and Persistence Behavior

State is in-memory only and is reset by `sm_destroy`. Session capacity is stored in `global_conf.sessions_cap` and mutated atomically as sessions are admitted and disconnected.

## Dependencies and Integration Points

It depends on GLib hash/list/locks, `management/tree_conn.h`, `management/user.h`, and `global_conf` from the config parser. Tree connection management calls it after access checks.

## Risks and Edge Cases

Capacity accounting is easy to regress: `sm_check_sessions_capacity` decrements only when a new session is needed, but `sm_handle_tree_disconnect` increments on every disconnect path in this file. Refcount and table removal are tightly coupled; races around lookup, put, and remove require lock coverage. Session objects store a user pointer without visibly taking a user reference here, so lifetime assumptions depend on the caller and shutdown ordering.

## Test Signals

Concurrent tree-connect/disconnect stress tests, capacity limit tests, duplicate session-ID races, missing-session disconnects, and shutdown with live tree connections are the main signals.
