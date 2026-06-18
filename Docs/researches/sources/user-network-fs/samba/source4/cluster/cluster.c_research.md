# sources/user-network-fs/samba/source4/cluster/cluster.c

## Purpose
Implements the public cluster abstraction dispatch layer. It forwards cluster ID creation, temporary database opening, backend handle access, and inter-node messaging calls to the currently installed `cluster_ops` backend, defaulting to local non-cluster operations.

## Important APIs, types, and functions
- File-scope `static struct cluster_ops *ops` stores the active backend.
- `cluster_set_ops()` installs a backend.
- `cluster_init()` lazily installs the local backend by calling `cluster_local_init()` if no backend exists.
- `cluster_backend_handle()`, `cluster_id()`, `cluster_db_tmp_open()`, `cluster_message_init()`, and `cluster_message_send()` are public wrappers.

## Control flow
Most public calls first ensure initialization, then call the corresponding function pointer. `cluster_backend_handle()` is the exception: it dereferences `ops` directly and assumes a backend was already installed.

## State and persistence behavior
The only state is the process-global backend pointer. Persistence is delegated to the backend, particularly temporary DB creation through `cluster_db_tmp_open()`. Messaging behavior is entirely backend-defined.

## Dependencies and integration points
Depends on `cluster.h`, `cluster_private.h`, generated server ID types, and the local backend from `local.c`. Other Samba subsystems use this file to avoid hard-coding CTDB/local differences.

## Risks and edge cases
- `cluster_backend_handle()` can crash if called before any other cluster API initializes `ops`.
- No locking protects backend installation, so dynamic backend changes are process-global and not thread-safe.
- Function pointer contracts are trusted; invalid backend structs will crash callers.

## Test signals
No direct tests are in this subset. Useful coverage would verify default local initialization, custom backend installation, and the pre-init behavior of `cluster_backend_handle()`.
