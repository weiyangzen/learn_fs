## sources/test-tools/filebench/fileset.h

### Purpose
`fileset.h` defines the public structures, flags, and function prototypes for Filebench filesets and fileset entries. It is the contract used by parser, flowop, filesystem, and statistics code to work with logical collections of files and directories.

### Important APIs, Types, And Functions
`filesetentry_t` represents a file, internal directory, or leaf directory with list links, parent pointer, embedded AVL link, index, path, depth, size, open count, flags, and back-pointer to its fileset. `fileset_t` stores workload parameters (`fs_name`, `fs_path`, entries, leafdirs, size, create/reuse/read-only flags), computed counts, locks, condition variables, AVL trees, rotors, lists, and histogram state. Flags define entry type and state (`FSE_TYPE_FILE`, `FSE_TYPE_DIR`, `FSE_TYPE_LEAFDIR`, `FSE_FREE`, `FSE_EXISTS`, `FSE_BUSY`, `FSE_REUSING`, `FSE_THRD_WAITNG`) plus pick semantics (`FILESET_PICK*`) and fileset attributes (`FILESET_IS_RAW_DEV`, `FILESET_IS_FILE`). Public prototypes expose create, define, find, pick, open, resolve, iterate, print, unbusy, histogram, and cleanup functions.

### Control Flow
The header establishes that callers define filesets, create/populate them, pick entries under runtime flowops, open files, then release entries through `fileset_unbusy`. The pick flags determine whether callers need files, directories, leaf directories, unique/free entries, existing entries, non-existing entries, or index-based selection.

### State And Persistence
`fileset_t` combines shared-memory runtime state with real filesystem intent. Its AVL trees classify entries by existence/free state, while idle counters and condition variables coordinate concurrent workers. Histogram pointers allow shared access tracking.

### Dependencies And Integration Points
It includes `filebench.h`, which supplies `avd_t`, `fbint_t`, `avl_node_t`, `avl_tree_t`, pthread types, and filesystem descriptor types through nested includes. `fileset.c` implements most prototypes; flowops consume `fileset_pick` and `fileset_openfile`.

### Risks
The structure is large and shared across modules, so layout changes have wide blast radius. `FSE_MAXPATHLEN` is only 16 for per-entry generated names, while full paths use `MAXPATHLEN` elsewhere. `fs_file_exrotor` is indexed by thread id up to `FSE_MAXTID`; callers must keep ids in range. Many fields are protected by `fs_pick_lock`, but the header relies on comments rather than type-enforced access.

### Test Signals
Tests should check flag combinations, pick semantics, AVL offset correctness for `fse_link`, shared-memory initialization, thread-id bounds, and compatibility of structure layout with parser and flowop code.
