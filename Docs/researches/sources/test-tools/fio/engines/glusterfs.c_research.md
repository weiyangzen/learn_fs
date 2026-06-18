# sources/test-tools/fio/engines/glusterfs.c

Purpose: Provides common GlusterFS gfapi option handling, connection sharing, and file lifecycle for `gfapi` and `gfapi_async` engines.

Important APIs/functions: Defines `gfapi_options`, `fio_gf_setup()`, `fio_gf_cleanup()`, `fio_gf_get_file_size()`, `fio_gf_open_file()`, `fio_gf_close_file()`, and `fio_gf_unlink_file()`. Internal helpers manage `glfs_info` instances with a global list and mutex for `single-instance` sharing.

Control flow: Setup allocates `gf_data`, obtains a glfs handle either by creating a new one or refcounting a shared volume/brick instance, and stores it on `td->io_ops_data`. New glfs handles call `glfs_new`, configure logging and volfile server, initialize, sleep, and verify root lstat. Open maps fio read/write/direct/sync options to gfapi flags, creates/opens the file, extends and fills read targets if too short, optionally fsyncs created content, and applies fadvise when compiled. Close closes the gfapi fd. Cleanup frees async arrays, closes fd, releases glfs handle, and frees data.

State/persistence: Global `glfs_list_head` stores shared glfs handles with refcounts. Per-thread `gf_data` stores one current fd and optional async event array. Files are created/extended/unlinked in GlusterFS.

Dependencies/integration: Requires GlusterFS libgfapi, fio file sizing/layout helpers, optional new gfapi APIs and fadvise support.

Risks: `fio_gf_unlink_file()` finalizes `g->fs` and frees `g` directly instead of using the shared refcount release path, which can conflict with single-instance mode. `fio_gf_put_glfs()` frees `volume`/`brick` but not the `glfs_info` struct itself. Single `g->fd` makes multi-file behavior fragile. There is a fixed `/tmp/fio_gfapi.log` path.

Test signals: Cover single-instance refcounting, multi-thread setup/cleanup, file extension for read jobs, create_fsync, unlink, direct/sync flags, and both old/new gfapi compile configurations.
