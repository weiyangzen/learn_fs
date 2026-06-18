# File Research: sources/os/linux/linux-stable/fs/squashfs/decompressor_multi.c

## Summary
Implements the dynamically allocated multi-stream decompressor threading mode.

## Key APIs
- Exports `squashfs_decompressor_multi`.

## Important Behavior
The mode creates one default decompressor stream at mount time, then allocates additional streams on demand up to `msblk->max_thread_num`, whose maximum is `num_online_cpus() * 2`.

Available streams live on `strm_list`. `get_decomp_stream()` removes one, allocates a new one if allowed, or waits for an existing stream to be returned. `put_decomp_stream()` requeues the stream and wakes a waiter.

## Synchronization
Uses a mutex to protect the stream list and stream count, plus a wait queue for callers blocked by the stream limit or allocation failure.

## Risks
Mount-time setup retains `comp_opts` in the stream object because later dynamic stream allocations need the same options. Destroy assumes no decompressions are still active and frees all idle streams and the retained options.
