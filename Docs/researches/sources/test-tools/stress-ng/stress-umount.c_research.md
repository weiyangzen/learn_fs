## sources/test-tools/stress-ng/stress-umount.c

Purpose: Implements `umount`, a Linux/CAP_SYS_ADMIN stressor that races mounting, unmounting, and `/proc/mounts` reading.

Important APIs/types/functions: `stress_umount_info`, `stress_umount_supported`, `stress_umount_umount`, `stress_umount_mounter`, `stress_umount_umounter`, `stress_umount_read_proc_mounts`, and `stress_umount_spawn`; uses `mount` or the fsopen/fsconfig/fsmount/move_mount API, `umount`/`umount2`, fork synchronization, and kill/reap helpers.

Control flow: creates a realpath temp mount point, spawns three synchronized children: one repeatedly mounts tmpfs/ramfs, one aggressively unmounts it, and one repeatedly reads `/proc/mounts`. Parent synchronizes starts, waits until the stressor stops, then kills all children and removes the temp directory.

State and persistence: transient mount state under a temp directory; cleanup forces unmount and removes the directory. Shared PID synchronization state is mmap-backed.

Dependencies/integration: needs Linux mount APIs and `CAP_SYS_ADMIN`; uses core capabilities, signal, and process synchronization.

Risks: high kernel/filesystem impact; permission, ENOSPC, ENOMEM, EBUSY, and unsupported new mount API paths are expected. Cleanup correctness is critical to avoid leaked mounts.

Test signals: `VERIFY_ALWAYS`; detects unexpected mount/umount errors, child setup failures, and uses bogo increments on successful mount cycles.
