# File Research: sources/os/linux/linux/fs/squashfs/decompressor_multi_percpu.c

Implements per-CPU decompression streams.

Create allocates one stream per possible CPU and initializes a `local_lock_t` for each. Decompression locks the current CPU’s stream, runs the selected wrapper, and unlocks.

This mode avoids central stream-list contention but preallocates per-CPU decompressor state. Its max decompressor count is `num_possible_cpus()`.
