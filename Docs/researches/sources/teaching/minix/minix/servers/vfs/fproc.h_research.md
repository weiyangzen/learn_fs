# File Research: sources/teaching/minix/minix/servers/vfs/fproc.h

Header defining per-process VFS state.

`struct fproc` contains:
- Process identity: PID and endpoint.
- Working and root directories.
- Descriptor table and close-on-exec bitset.
- Controlling TTY.
- Blocking state and per-blocking-type saved arguments for pipes, pipe open, flock, character device, and socket device operations.
- Real/effective UID/GID and supplementary groups.
- Umask.
- Process mutex, active worker, pending function, and pending messages.
- Last exec name.
- Optional lock-debug counters.

Defines:
- Blocking-state union shortcut macros: `fp_pipe`, `fp_popen`, `fp_flock`, `fp_cdev`, `fp_sdev`.
- `fp_flags` values:
  - `FP_SRV_PROC`
  - `FP_REVIVED`
  - `FP_SESLDR`
  - `FP_PENDING`
  - `FP_EXITING`
  - `FP_PM_WORK`
- `PID_FREE`, `REVIVING`, `NOT_REVIVING`.
- `struct fproc_light`, a small exported view for MIB/system information.
