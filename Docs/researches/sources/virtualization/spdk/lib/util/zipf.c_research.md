# File Research: sources/virtualization/spdk/lib/util/zipf.c

This file implements a Zipf-distributed integer generator.

`spdk_zipf_create()` allocates generator state, stores range and theta, computes alpha, zeta over the range, eta, and a limit for returning value 1. The zeta calculation sums exactly for up to 10 million entries and approximates larger tails in 1 million-entry chunks using averaged increments.

`spdk_zipf_generate()` draws a uniform random value with `spdk_rand_xorshift64()`, scales it by `zetan`, returns 0 or 1 for the first two regions, or computes the general Zipf value and wraps it by `range`. `spdk_zipf_free()` frees and nulls the caller’s pointer.

A notable behavior is that `spdk_zipf_create(uint64_t range, double theta, uint32_t seed)` ignores the supplied `seed` parameter and instead initializes `zipf->seed` from `spdk_rand_xorshift64_seed()`. Also, the code assumes sensible nonzero range and theta values; it does not validate them.
