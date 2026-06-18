## sources/test-tools/filebench/fb_localfs.c

### Purpose
`fb_localfs.c` implements the default local filesystem plugin for Filebench. It fills `fs_functions_vec` with POSIX-backed operations and, when AIO support is available, registers local-filesystem-specific async write/wait flowops.

### Important APIs, Types, And Functions
External functions are `fb_lfs_funcvecinit` and `fb_lfs_newflowops`. The static `fb_lfs_funcs` vector maps Filebench filesystem operations to wrappers for open, read, pread, write, pwrite, lseek, truncate, rename, close, link, symlink, unlink, readlink, mkdir, rmdir, opendir/readdir/closedir, fsync, stat/fstat, access, freemem, and recursive remove. Under `HAVE_AIO`, `fb_lfsflow_aiowrite`, `fb_lfsflow_aiowait`, `aio_allocate`, and `aio_deallocate` manage asynchronous writes.

### Control Flow
Initialization points the global filesystem vector at local wrappers and optionally registers AIO flowops. Most wrappers directly call the corresponding POSIX function, using configured `*64` aliases from `filebench.h`. `fb_lfs_freemem` maps chunks of a file and invalidates them with `msync(MS_INVALIDATE)`. AIO write sets up a random offset through `flowoplib_iosetup`, allocates an `aiolist_t`, fills `aiocb64`, submits `aio_write64`, and records flowop timing. AIO wait reaps roughly half of outstanding requests or one minimum, using either `aio_waitn64` or polling `aio_error64`.

### State And Persistence
The filesystem vector is global process state. AIO state is stored on each threadflow's `tf_aiolist`. The wrappers operate on external filesystem state and file descriptors in `fb_fdesc_t`. No separate persistence is maintained by the plugin.

### Dependencies And Integration Points
It depends on `filebench.h`, `fsplug.h`, `flowop.h`, `threadflow.h`, and POSIX filesystem/AIO headers. `fileset.c` and `flowop_library.c` call through the `FB_*` macros backed by `fs_functions_vec`.

### Risks
`fb_lfs_recur_rm` constructs `rm -rf %s` with `snprintf` and `system`, so paths with shell metacharacters are dangerous. AIO list handling has duplicated `break` and does not free deallocated `aiolist_t` nodes, which may leak during long runs. `fb_lfs_freemem` does not check `mmap64` failure before `msync`/`munmap`. Most wrappers return raw system errors and leave interpretation to callers.

### Test Signals
Tests should verify vector initialization, all wrapper return paths, recursive removal safety with controlled paths, AIO submit/reap behavior when enabled, direct I/O/fadvise integration through fileset opens, and portability paths where 64-bit or AIO functions are macro-mapped.
