<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fsplug.h -->
# sources/test-tools/filebench/fsplug.h

Purpose: defines Filebench's filesystem plugin abstraction. Built-in flowops call `FB_*` macros instead of direct POSIX calls so local, NFS, CIFS, or other client backends can share WML flowop semantics.

Important APIs/types: `fb_plugin_type_t` enumerates `LOCAL_FS_PLUG`, `NFS3_PLUG`, `NFS4_PLUG`, and `CIFS_PLUG`. `fb_fdesc_t` is a union of OS fd integer or backend pointer. `fsplug_func_t` contains function pointers for memory advice, open/read/write/pread/pwrite/lseek/truncate/rename/close/link/symlink/unlink/readlink/mkdir/rmdir/opendir/readdir/closedir/fsync/stat/fstat/access/recursive remove. `fs_functions_vec` is the active dispatch table.

Control flow: `flowop_init()` selects the active vector from `filebench_shm->shm_filesys_type`; `flowop_library.c` invokes `FB_OPEN`, `FB_PREAD`, `FB_WRITE`, and related macros, which indirect through `fs_functions_vec`.

State/persistence: the active vector is process-global, while descriptors are stored per threadflow in `fb_fdesc_t` slots. Backend-specific persistent state can live behind `fd_ptr`.

Dependencies/integration: includes `filebench.h` for platform types and is consumed heavily by flowop libraries and fileset operations. Local filesystem support is installed by `fb_lfs_funcvecinit()`.

Risks: macros do not check that `fs_functions_vec` or individual callbacks are non-null, so initialization order is critical. The union descriptor requires each backend to consistently set and test the correct member; code frequently checks `fd_ptr` even for local fds.

Test signals: plugin initialization tests should assert all callbacks used by built-in flowops are populated. Backend smoke tests should compare local POSIX behavior with macro-dispatched behavior for all file and directory operations.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fsplug.h -->
