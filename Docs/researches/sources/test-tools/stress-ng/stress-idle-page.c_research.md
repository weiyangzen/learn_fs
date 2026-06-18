# sources/test-tools/stress-ng/stress-idle-page.c

## Purpose
`stress-idle-page.c` stresses Linux idle page tracking by writing and reading chunks of `/sys/kernel/mm/page_idle/bitmap` while scanning through the bitmap.

## Important APIs, Types, And Functions
`bitmap_file` points to the kernel idle-page bitmap. `stress_idle_page_supported()` requires `CAP_SYS_RESOURCE`, effective root, and read access to the bitmap. `stress_idle_page()` opens the bitmap read-write, writes 64 `uint64_t` words of all ones to mark pages idle, seeks back, reads the same region, advances the offset, handles `ENXIO` by wrapping to zero, and increments bogo ops.

## Control Flow
On Linux, support checking is stricter than the compile gate. Runtime opens the sysfs bitmap, initializes the set buffer, waits at the sync barrier, then loops over seek/write/seek/read at the current offset. If the kernel reports `ENXIO`, scanning wraps to the start. A guard aborts if the seek position stops advancing.

## State And Persistence
The stressor mutates kernel idle-page tracking state via sysfs but creates no regular files. Local state is the bitmap fd, current offset, last offset, and stack buffers.

## Dependencies And Integration Points
It is Linux-only and depends on stress-ng capability checks, process state/sync helpers, and standard `open`, `lseek`, `read`, and `write`.

## Risks
Requires root and a kernel configured with idle page tracking. Writing the bitmap affects idle-page accounting for the running system. Offset handling must avoid infinite loops on short or non-advancing scans. Access failures should skip rather than fail.

## Test Signals
Expected signals are support skip without root/capability/sysfs file, successful read-write scans on configured kernels, wrap on `ENXIO`, bogo increments while advancing, and early abort if the offset stalls.
