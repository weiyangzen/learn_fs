# sources/test-tools/stress-ng/stress-link.c

Purpose: implements both hard-link `link` and symbolic-link `symlink` stressors through a shared link creation/removal engine, including optional directory fsyncs and symlink readback checks.

Important APIs/types/functions: `stress_link_generic()` receives either `link` or `symlink`, a function name, and sync option. `stress_link_unlink()` removes generated paths. `stress_mount_get()`/`stress_mount_free()` provide mount points for cross-device hard-link probes. `stress_link_info` and `stress_symlink_info` register separate stressors.

Control flow: the generic path creates a temp directory and source file, optionally opens the directory for sync, gathers mount points, sync-starts, and loops creating up to 8192 links. Symlink mode verifies `readlink` and optional `readlinkat` contents and lengths. Hard-link mode attempts cross-mount links to exercise `EXDEV` paths. The loop also probes `pathconf`, invalid `readlink` and `readlinkat` calls, optionally fsyncs the directory, removes generated links, increments bogo ops, and repeats.

State and persistence behavior: temp source file, generated links, optional external temp newpath, and temp directory are removed. Symlinks and hard links are transient but can be numerous during a loop.

Dependencies and integration points: uses stress-ng filesystem temp helpers, mount enumeration, builtin wrappers, settings, and metrics. Hard-link registration is disabled on Haiku; symlink remains registered. Both are `CLASS_FILESYSTEM | CLASS_OS` with always-on verification.

Risks: link limits, quota, minix-like unlink contention, cross-device behavior, and permission constraints produce many expected errors. If interrupted during unlink, cleanup speed can dominate runtime.

Test signals: run hard-link and symlink modes with sync options, on filesystems with low link limits and multiple mounts, and verify source/created links are fully removed and symlink readback catches path corruption.
