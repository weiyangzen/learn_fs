# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi_percpu.c

## Summary
Implements the percpu decompressor threading mode, with one decompressor stream per possible CPU.

## Key APIs
- Exports `squashfs_decompressor_percpu`.

## Important Behavior
Mount setup allocates a percpu `squashfs_stream` array and initializes one backend stream for each possible CPU. Decompression uses `local_lock()` and `this_cpu_ptr()` so each CPU serializes access to its local backend stream.

`max_decompressors()` reports `num_possible_cpus()`.

## Risks
Allocation cost scales with possible CPUs, not online CPUs. The cast between percpu pointer and `void *` in `msblk->stream` is deliberate and must be reversed consistently in destroy/decompress paths.
