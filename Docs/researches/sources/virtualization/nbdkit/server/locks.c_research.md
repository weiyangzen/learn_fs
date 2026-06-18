# File Research: sources/virtualization/nbdkit/server/locks.c

Purpose: Implements locking policy derived from nbdkit’s selected plugin/filter thread model.

State:
- Global `thread_model` caches `top->thread_model(top)` after configuration.
- `connection_lock` serializes whole connections for `serialize_connections`.
- `all_requests_lock` serializes all requests for `serialize_all_requests`.
- `unload_prevention_lock` is an rwlock that prevents backend unload while requests are active.

Public helpers:
- `name_of_thread_model` converts thread-model constants to strings.
- `lock_init_thread_model` selects and logs the effective model.
- `lock_connection`/`unlock_connection` enforce connection serialization when required.
- `lock_request`/`unlock_request` enforce all-request or per-connection request serialization and hold an unload-prevention read lock.
- `lock_unload`/`unlock_unload` take the unload-prevention write lock.

Lock ordering:
- Request locking first applies global serialization, then per-connection serialization, then unload prevention.
- Unlocking releases in reverse for unload, per-connection, and global locks.
