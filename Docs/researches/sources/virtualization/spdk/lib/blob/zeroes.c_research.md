# File Research: sources/virtualization/spdk/lib/blob/zeroes.c

Implements a singleton read-only `spdk_bs_dev` that represents an infinite zero-filled backing device. Reads and readv fill the supplied buffer/iovecs with zeroes and complete successfully. Extended readv can use `spdk_memory_domain_memzero()` when a memory domain is supplied, falling back to local `memset()` otherwise.

All mutating operations, including write, writev, writev_ext, write_zeroes, and unmap, complete with `-EPERM` and assert false. The device reports every range as valid and zero-filled, has `UINT64_MAX` 512-byte blocks, and cannot translate LBAs to a physical base.

`bs_create_zeroes_dev()` returns the global device instance, and `blob_backed_with_zeroes_dev()` checks whether a blob’s backing device is that singleton.
