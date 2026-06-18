# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/reallocarr.c

Implements `reallocarr(void *ptr, size_t number, size_t size)`, where `ptr` points to the allocation pointer to update. It preserves caller `errno`, frees and clears the pointer for zero count or zero size, checks multiplication overflow before reallocating, and only stores the new pointer on success.

Return value is an error number rather than `errno`-style `-1`: `0` on success, `EOVERFLOW` for size overflow, or the allocation failure `errno`.
