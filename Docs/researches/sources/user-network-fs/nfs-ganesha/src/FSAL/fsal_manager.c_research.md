## sources/user-network-fs/nfs-ganesha/src/FSAL/fsal_manager.c

### Purpose
`fsal_manager.c` owns FSAL module lifecycle: global registration state, loading static and dynamic FSALs, parsing FSAL config blocks, looking up modules, registering/unregistering modules, and initializing sub-FSALs.

### Important APIs, Types, And Functions
Global state includes `pthread_mutex_t fsal_lock`, `GLIST_HEAD(fsal_list)`, loader status variables `dl_error`, `so_error`, `new_fsal`, and `load_state`. Public functions include `initialize_fsal_lock`, `destroy_fsal_lock`, `load_fsal_static`, `start_fsals`, `load_fsal`, `lookup_fsal`, `register_fsal`, `unregister_fsal`, `fsal_init`, `fsal_load_init`, and `subfsal_commit`. Config integration is represented by `fsal_block`, `fsal_dummy_block`, `fsal_name_adder`, and the weak `start_custom_static_fsals`.

### Control Flow
Startup initializes locks and context refstrings, parses `FSAL_LIST`, transitions the loader to idle, and loads static `MDCACHE` and `PSEUDO` FSALs before optional custom static FSALs. Dynamic loading constructs `libfsal<name>.so`, lowercases the basename, stats it, enters `loading`, calls `dlopen`, then accepts registration from a constructor or falls back to `dlsym("fsal_init")`. Successful registration leaves the new module in `new_fsal`; `load_fsal` takes an initial reference, stores path and `dl_handle`, and returns the handle. `register_fsal` validates API versions, copies `def_fsal_ops`, initializes lists/locks, inserts into `fsal_list`, and optionally registers pNFS FSAL ID. `fsal_load_init` looks up or loads by name, calls `init_config` or `update_config`, marks `is_configured`, and registers NFS backend services.

### State And Persistence
The file manages process-global FSAL module state only. It protects the module list and loader state with `fsal_lock`, initializes `fs_lock` for local filesystem tracking when available, stores module path/name strings, shared-object handles, refcounts, and configuration status.

### Dependencies And Integration Points
It depends on `default_methods.c` through `def_fsal_ops`, config parsing, NFS core parameters for module location, pNFS utilities, localfs locking, FSAL commonlib registration, and static FSAL init functions from `fsal_private.h`. Export parsing and sub-FSAL configuration call `fsal_load_init`.

### Risks
The loader state machine is global, so concurrent or reentrant loads depend on strict `fsal_lock` discipline. `dl_error` sometimes points to `dlerror()` storage and sometimes duplicated storage, so ownership must remain consistent. `load_fsal` calls `LogFatal` on `dlopen` failure, making missing modules fatal in that path. Version checks allow older minor versions but reject newer minors. Registration copies only module ops; FSAL-specific export/object defaults must be handled elsewhere. Static loading requires `load_state == idle`, while constructors during process init use `init`, making startup ordering important.

### Test Signals
Tests should cover static FSAL load, dynamic constructor registration, manual `fsal_init` fallback, missing library/symbol failures, version mismatch, duplicate or invalid load states, case-insensitive lookup with refcount increment, init/update config paths, unregister with nonzero refcount, and pNFS FSAL ID table registration.
