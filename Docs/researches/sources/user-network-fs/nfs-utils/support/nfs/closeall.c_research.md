# sources/user-network-fs/nfs-utils/support/nfs/closeall.c

Purpose: close all file descriptors greater than or equal to a caller-supplied minimum.

Important API: `void closeall(int min)`.

Control flow: prefers iterating `/proc/self/fd`, parsing numeric directory entries and closing each descriptor except the directory handle itself. If `/proc/self/fd` cannot be opened, it falls back to `sysconf(_SC_OPEN_MAX)` and closes descending descriptors down to `min`.

State and persistence: mutates the process descriptor table; no persistent state.

Dependencies and integration: used during daemonization to close inherited descriptors. Depends on procfs availability for efficient operation.

Risks: closing descriptors while other threads are active is process-wide and can race. The procfs path sees a snapshot during directory iteration, so descriptors opened concurrently may survive. The fallback assumes `sysconf(_SC_OPEN_MAX)` is usable as an integer upper bound.

Test signals: descriptors below/above `min`, procfs unavailable fallback, very high descriptor numbers, and preservation of the `/proc/self/fd` directory fd.
