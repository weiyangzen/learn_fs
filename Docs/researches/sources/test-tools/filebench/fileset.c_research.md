## sources/test-tools/filebench/fileset.c

### Purpose
`fileset.c` implements Filebench filesets: logical trees of files and directories used by workloads. It defines, populates, preallocates, picks, opens, marks busy/unbusy, prints, and deletes fileset entries while tracking membership in AVL trees.

### Important APIs, Types, And Functions
Public APIs include `fileset_define`, `fileset_createsets`, `fileset_delete_all_filesets`, `fileset_openfile`, `fileset_pick`, `fileset_unbusy`, `fileset_resolvepath`, `fileset_find`, `fileset_iter`, `fileset_print`, plus declared-but-not-present-in-this-file histogram functions from the header. Important internal helpers include `fileset_mkdir`, `fileset_create_subdirs`, `fileset_alloc_file`, `fileset_alloc_leafdir`, `fileset_pickreset`, `fileset_find_entry`, `fileset_create`, `fileset_populate_file`, `fileset_populate_leafdir`, `fileset_populate_subdir`, `fileset_populate`, and `fileset_checkraw`.

### Control Flow
Workloads call `fileset_define` during parsing to allocate a shared fileset and link it to `shm_filesetlist`. `fileset_createsets` validates all definitions once, handles raw devices, calls `fileset_populate` to construct in-memory entries, then `fileset_create` to create directories and preallocate selected files/leaf directories. Population recursively builds directory/file entries based on entry counts, leaf directory counts, directory width, depth, and gamma/random variables. Runtime flowops call `fileset_pick` to choose a file/dir/leafdir from the appropriate AVL tree, blocking on condition variables if no idle entries are available. Callers eventually call `fileset_unbusy`, which updates existence flags, moves entries between AVL trees, adjusts idle counts, and signals waiters.

### State And Persistence
Filesets and entries are allocated in Filebench shared memory and mirrored to real filesystem state when created. Each `fileset_t` maintains lists, AVL trees for free/existing/non-existing files and leafdirs, directory trees, idle counters, condition variables, pick locks, rotors, and byte/file counts. Persistent side effects are actual directories/files under `fs_path/fs_name`; deletion calls recursive remove unless raw-device mode is active.

### Dependencies And Integration Points
It depends on `filebench.h`, `fileset.h`, `gamma_dist.h`, `utils.h`, and `fsplug.h`. It calls through `FB_*` filesystem plugin macros implemented by `fb_localfs.c` by default. Parser code creates filesets, flowops pick/open entries, `fb_random64` provides random selection, and `fb_avl` stores membership indexes.

### Risks
`filecreate_done` is global, so filesets defined after creation are ignored, as the code comment notes. Recursive directory population can be deep depending on random parameters. `fileset_resolvepath` allocates paths that callers must free. `fileset_create` uses `rand()` for preallocation selection without explicit seeding in this file. Parallel preallocation uses shared counters and detached threads; failures are signaled through `shm_fsparalloc_count = -1`. Path construction relies on fixed `MAXPATHLEN` buffers. Underlying recursive remove safety depends on the filesystem plugin.

### Test Signals
Tests should cover define/find/iterate, raw-device detection, populate counts and AVL membership, pick/unbusy transitions for existing/non-existing/free entries, create/reuse/trust-tree behavior, parallel preallocation success/failure, open flags for direct/sync/fadvise, and deletion cleanup. Integration tests need real temporary directories and the local filesystem plugin.
