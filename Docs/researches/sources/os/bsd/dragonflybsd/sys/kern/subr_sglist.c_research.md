# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_sglist.c

## Summary
Implements scatter/gather list allocation and construction from physical, kernel virtual, user virtual, mbuf, and uio ranges.

## Main Responsibilities
- Allocates, frees, clones, builds, and measures `struct sglist`.
- Appends contiguous physical ranges and coalesces adjacent physical segments.
- Translates kernel/user virtual buffers through `pmap_kextract()` or `pmap_extract()`.
- Appends mbuf chains and uio vectors.
- Consumes uio data while updating iov base/length, residual, and offset.
- Splits, joins, and slices scatter/gather lists.

## Important Behavior
Append operations save the original segment count and last-segment length so failures can roll back partial changes. User and uio paths require a valid thread/pmap for `UIO_USERSPACE`. `sglist_split()` refuses to modify shared lists with refcount greater than one.

## Risks
Segment capacity exhaustion returns `EFBIG`; callers must size lists correctly or handle partial consume behavior. Physical contiguity is detected only by adjacent physical addresses. Split/join/slice APIs require empty destination lists when provided.
