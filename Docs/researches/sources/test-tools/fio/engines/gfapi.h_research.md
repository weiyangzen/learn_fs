# sources/test-tools/fio/engines/gfapi.h

Purpose: Shared declarations for GlusterFS gfapi fio engines.

Important APIs/types: Defines `gf_options` for volume, brick, and single-instance mode, plus `gf_data` for `glfs_t *fs`, `glfs_fd_t *fd`, and async completion array. Declares shared option table and common setup/cleanup/file callbacks implemented in `glusterfs.c`.

Control flow: Sync and async engine files include this header, use the shared options, call `fio_gf_setup()` during init, and delegate file lifecycle to common helpers.

State/persistence: `gf_data` is per-thread engine state; single-instance global sharing is implemented in `glusterfs.c`, not the header.

Dependencies/integration: Includes GlusterFS gfapi headers and fio core headers.

Risks: Exposes a single `fd` in `gf_data`, which constrains or complicates multi-file jobs. Header consumers must link with `glusterfs.c`.

Test signals: Build both gfapi engines and verify shared options populate `gf_options` consistently.
