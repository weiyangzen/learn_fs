# sources/test-tools/fio/engines/glusterfs_sync.c

Purpose: Implements the synchronous GlusterFS gfapi fio engine `gfapi`.

Important APIs/functions: Uses common gfapi setup/file callbacks and defines `fio_gf_prep()` plus `fio_gf_queue()`. Registers engine flags `FIO_SYNCIO | FIO_DISKLESSIO`.

Control flow: Prep seeks the gfapi fd to the IO offset when the next read/write offset is not already the file's last engine position. Queue handles reads with `glfs_read`, writes with `glfs_write`, sync with `glfs_fsync`, datasync with `glfs_fdatasync`, and rejects unsupported directions. It updates `engine_pos`, sets residuals for short positive transfers, and logs errors through fio.

State/persistence: Uses shared per-thread `gf_data` and `fio_file.engine_pos` for seek avoidance. File content persists in GlusterFS.

Dependencies/integration: Depends on gfapi sync APIs and common `glusterfs.c`.

Risks: Uses a single `g->fd`; multi-file jobs may not behave correctly. Short reads/writes are treated as successful residuals. New/old gfapi sync prototypes are compile-time selected.

Test signals: Test sequential seek optimization, random offset seeks, short transfer handling, sync/datasync paths, and multi-file workloads.
