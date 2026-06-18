## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_private.h

### Purpose
`fsal_private.h` is the private bridge among FSAL core implementation files. It exposes default operation vectors, the global FSAL registry lock/list, lock lifecycle functions, and statically linked FSAL initialization entry points.

### Important APIs, Types, And Functions
It declares `extern struct fsal_ops def_fsal_ops`, `extern struct export_ops def_export_ops`, `extern struct fsal_obj_ops def_handle_ops`, and `extern struct fsal_pnfs_ds_ops def_pnfs_ds_ops`. It declares `extern pthread_mutex_t fsal_lock`, `extern struct glist_head fsal_list`, `initialize_fsal_lock`, `destroy_fsal_lock`, `pseudo_fsal_init`, and `mdcache_fsal_init`.

### Control Flow
There is no executable control flow. Including files use these declarations to share process-global FSAL state and default method vectors without exposing them as public FSAL API.

### State And Persistence
The header declares process-global state owned by `fsal_manager.c` and default vectors owned by `default_methods.c`. It does not define or persist data itself.

### Dependencies And Integration Points
`fsal_manager.c` defines `fsal_lock` and `fsal_list`; `default_methods.c` defines the default vectors; `fsal_destroyer.c` walks `fsal_list` and destroys locks; static startup calls `mdcache_fsal_init` and `pseudo_fsal_init`.

### Risks
This header intentionally exposes mutable globals inside the FSAL implementation boundary. Any new internal user must obey locking rules for `fsal_list` and must not treat default vectors as immutable API contracts beyond their versioned FSAL ABI role. Adding vector declarations here must stay synchronized with `default_methods.c` and registration code.

### Test Signals
Build coverage is the main signal: all FSAL core objects must link against one definition of each extern. Lifecycle tests should indirectly validate that users of `fsal_lock`, `fsal_list`, and default vectors agree on initialization and destruction order.
