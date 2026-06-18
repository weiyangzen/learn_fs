# File Research: sources/virtualization/spdk/lib/dma/dma.c

Implements SPDK memory-domain registration and data-transfer dispatch. A global tail queue of `spdk_memory_domain` objects is protected by `g_dma_mutex`; a constructor registers the built-in `"system"` DMA domain.

`spdk_memory_domain_create()` validates optional context sizing, allocates the domain plus optional user-context tail storage, duplicates the id string, copies the public context prefix, copies user context bytes, assigns the device type, and inserts the domain in the global list. Destroy removes non-system domains and frees context/id memory.

Setter APIs install callbacks for translation, invalidation, pull, push, transfer, and memzero. Accessors expose context, user context, DMA device type, and DMA device id. Data movement APIs validate required arguments and return `-ENOTSUP` when the corresponding callback is absent.

Iteration helpers find the first or next domain, optionally filtered by id. `spdk_dma_device_type_get_name()` maps built-in RDMA, DMA, ACCEL, vendor-specific, and unknown type values to strings.
