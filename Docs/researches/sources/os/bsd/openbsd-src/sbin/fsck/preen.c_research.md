# File Research: sources/os/bsd/openbsd-src/sbin/fsck/preen.c

Implements `/etc/fstab` traversal and preen-mode scheduling for the generic `fsck` front-end.

Core model:
- Builds per-disk queues of partitions to check, using a disk base name derived by trimming trailing partition digits.
- Runs pass 1 filesystems immediately and serially.
- In preen mode, queues later-pass filesystems by disk and runs checks in parallel across disks, never concurrently checking multiple partitions on the same disk.
- Honors `-l maxparallel`, defaulting to the number of disks.

Important structures:
- `partentry` stores filesystem type, device name, mount point, and caller auxiliary data.
- `diskentry` stores one disk base name, its partition queue, and the active child pid.
- `badh` accumulates failed filesystems for final reporting.

Important functions:
- `checkfstab` loops pass numbers, applies the caller’s fstab filter, normalizes device names with `blockcheck`, runs or queues checks, waits for children, and reports aggregate failures.
- `finddisk` groups device names into disk queues.
- `addpart` appends a filesystem to a disk queue and warns about duplicate fstab devices.
- `startdisk` starts the next queued filesystem check for a disk and records its pid.

This file is responsible for safe preen parallelism and pass-order handling, not filesystem-specific repair logic.
