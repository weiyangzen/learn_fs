# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk.c

Main implementation of the VMware VDDK nbdkit plugin. It dynamically loads VDDK, parses local/remote VMDK connection parameters, opens disks, and delegates I/O to a per-connection worker thread.

Key behavior:
- Defines global VDDK function pointers by expanding `vddk-stubs.h`.
- Supports debug flags `vddk.diskinfo`, `vddk.extents`, and `vddk.datapath`.
- Parses configuration for compression, VDDK config file, cookie/session auth, create options, export wildcard, file path, libdir, NFC host port, reexec control, password, port, server, single-link, snapshot, thumbprint, transports, unbuffered, user, and VM spec.
- `.config_complete` rejects simultaneous `file` and `export`, detects remote mode from remote parameters, validates required local/remote options, restricts `create=true` to local files, requires `create-size`, and restores `LD_LIBRARY_PATH` after any re-exec.
- `load_library` searches preferred VDDK sonames from version 9 down to 6 under `libdir`, loads the first available with `dlopen`, records `library_version`, calls `reexec_if_needed(dirname(path))`, and resolves all required symbols.
- `.get_ready` loads VDDK and logs a Linux hint for a known VDDK >= 8 `/sys/class/scsi_disk` crash condition.
- `.after_fork` calls `VixDiskLib_InitEx` after nbdkit has forked, because VDDK creates background threads.
- VDDK log/warn/panic callbacks are routed to nbdkit debug/error, with selected CEIP/phone-home messages demoted to debug.
- `.dump_plugin` attempts non-fatal library loading, reports default libdir, library version, resolved library path when `dladdr` is available, transport modes, and found VDDK symbols.
- Thread model is `NBDKIT_THREAD_MODEL_PARALLEL`. `open_close_lock` serializes VixDiskLib open/close operations.
- `.open` allocates a handle, initializes command queue primitives, chooses filename from either fixed `file` or client export name matching `export` wildcard, allocates VDDK connection params, fills remote credentials when needed, connects, optionally creates a local VMDK once, opens the disk with read-only/single-link/unbuffered/compression flags, logs transport mode, and starts `vddk_worker_thread`.
- `.close` sends a `STOP` command to the worker, joins it, frees cached extents, closes/disconnects/free-params through VDDK, destroys synchronization primitives, and frees the handle.
- `.get_size` asks the worker for `VixDiskLib_GetInfo`, caches size as sectors * 512, and frees the info.
- `.block_size` reports 512-byte minimum, preferred max of logical sector, physical sector, and 4096, and max `0xffffffff`.
- `.can_fua`/`.can_flush` advertise native flush support.
- `.pread`, `.pwrite`, `.flush`, `.can_extents`, and `.extents` build command objects and synchronously wait for the worker. `.pwrite` implements FUA by issuing a flush after successful write.

Dependencies:
- VDDK shared libraries loaded at runtime.
- `vddk.h`, `vddk-stubs.h`, `worker.c`, `reexec.c`, `stats.c`.
- `dlopen`, `dlsym`, pthreads, optional `fnmatch`.

Notes and risks:
- Local file paths are not canonicalized because remote VDDK file paths may live on VMware hosts; local callers must provide absolute paths.
- VDDK can segfault on missing remote parameters, so remote validation is deliberately strict.
- `VixDiskLib_PrepareForAccess` is noted as missing.
- The plugin assumes VDDK sector-aligned I/O; alignment enforcement is in the worker.
