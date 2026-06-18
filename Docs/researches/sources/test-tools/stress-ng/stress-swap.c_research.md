# sources/test-tools/stress-ng/stress-swap.c

## Purpose
Implements the `swap` stressor, which creates temporary swap files, writes valid and intentionally malformed swap headers, exercises `swapon()` and `swapoff()`, and optionally asks the kernel to page out this process's mappings. It is Linux/Unix swap-subsystem pressure rather than a generic memory allocator stressor.

## Important APIs, Types, And Functions
`stress_swap_info_t` models the Linux `SWAPSPACE2` header fields used by the stressor. `stress_swap_supported()` requires `CAP_SYS_ADMIN`. `stress_swap_self()` parses `/proc/self/maps` and uses `MADV_PAGEOUT` on suitable mappings. `stress_swap_zero()` writes page-sized zero blocks to establish the file. `stress_swap_set_size()` writes swap metadata, UUID, volume label, last page, bad-page count, and signature, optionally corrupting selected fields. `stress_swap_check_swapped()` tracks `/proc/vmstat` `pswpout` deltas for metrics. `stress_swap_clean_dir()` forcibly swapoffs and removes stale regular files in the stressor temp directory. `stress_swap_child()` owns the main swapon/swapoff loop and page-integrity checks.

## Control Flow
The public `stress_swap()` runs `stress_swap_child()` under `stress_oomable_child()` and performs final directory cleanup. The child decides whether `swap-self` is active, maps a reusable page, removes stale temp files, creates a temp directory and swap file, disables CoW on Linux filesystems where possible, and preallocates a maximum-size swap file. After the sync barrier it repeatedly chooses a random swap size, random swap flags, and occasionally a bad header mode. It writes the header, calls `swapon()`, maps anonymous memory sized to the current swap, writes per-page address sentinels, optionally pageouts the mapping and self mappings, verifies sentinel values, unmaps, then calls swapoff. It also probes invalid swapon/swapoff filenames and invalid flags before incrementing bogo operations.

## State And Persistence
Persistent state is intentionally temporary: a per-worker temp directory and swap file are created and unlinked/removed during cleanup. Kernel state may briefly include an active swap device, memory pages moved to swap, VM counters, and filesystem flags such as no-CoW. Cleanup paths close the file, unlink it, remove the temp dir, call swapoff on stale files, and unmap the page buffer. `stress_swap_check_swapped()` has a static previous counter within the process.

## Dependencies And Integration Points
Requires build support for `sys/swap.h` and `swap`; otherwise the exported stressor is `stress_unimplemented`. Runtime requires `CAP_SYS_ADMIN`, `swapon`, `swapoff` via `stress_memory_swap_off`, mmap, fallocate/write/lseek, `/proc/vmstat`, optional `/proc/self/maps`, Linux ioctls for no-CoW, madvise/pageout helpers, filesystem temp helpers, and OOMable child orchestration.

## Risks And Test Signals
This is privilege-sensitive and can fail because of missing capability, unsupported filesystem type, existing swapfile limits, low disk space, CoW filesystems, or kernels rejecting swap flags/header variants. Bad headers are expected to fail and should not be reported as stressor failures. Good headers failing with EPERM, EINVAL, EBUSY, or ENOSPC are handled specially. Test signals are bogo progress, no active swapfiles left behind, successful sentinel preservation after swap pressure, pages-swapped-out metric updates, and skip behavior on unsupported or underprivileged systems.
