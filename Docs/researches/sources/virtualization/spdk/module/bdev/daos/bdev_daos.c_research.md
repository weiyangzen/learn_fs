# File Research: sources/virtualization/spdk/module/bdev/daos/bdev_daos.c

This file implements an SPDK bdev backed by a DAOS DFS object. Each bdev corresponds to a named object in a DAOS pool/container and maps SPDK block offsets to byte offsets in DFS reads, writes, and punches.

The bdev object `struct bdev_daos` embeds `spdk_bdev`, stores the DAOS object class, pool/container labels, and reset retry state. Each IO channel owns DAOS handles for pool, container, DFS mount, DFS object, DAOS event queue, and a poller. Each IO task embeds a DAOS event, remembers the submitting SPDK thread, original bdev IO, status, offset, DAOS iovs, and an SGL.

DAOS client initialization is reference-counted globally with a mutex around `daos_init()`/`daos_fini()`. Bdev creation validates nonzero block count, block size aligned to 512, nonempty name/pool/container, object class name, and label lengths. It initializes DAOS once, simulates channel creation and destruction to verify pool/container/object access before registering an unusable bdev, then registers an IO device and the bdev.

Channel creation connects to the DAOS pool, opens the container, mounts DFS, opens or creates the named object, creates a DAOS event queue, and starts a poller. Channel destruction unregisters the poller, force-destroys the event queue, releases the DFS object, unmounts DFS, closes the container, disconnects the pool, and decrements the DAOS engine reference.

Read and write convert SPDK iovs to DAOS `d_iov_t` arrays capped at `SPDK_BDEV_IO_NUM_CHILD_IOV`, initialize an async DAOS event on the channel queue, fill an SGL, store the byte offset, and call `dfs_read()` or `dfs_write()`. The channel poller calls `daos_eq_poll()` with `DAOS_EQ_NOWAIT`, finalizes completed events, maps DAOS event errors to IO status, and completes the original bdev IO on the submitting SPDK thread if completion is observed on another thread.

Supported IO types are READ, WRITE, RESET, FLUSH, and UNMAP. READ uses `spdk_bdev_io_get_buf()` before submission. FLUSH is a no-op because the file treats completed DAOS writes as persistent. UNMAP calls `dfs_punch()` for the requested byte range. RESET cannot cancel DAOS requests, so it repeatedly walks channels and checks `daos_eq_query(..., DAOS_EQR_WAITING, ...)` until no in-flight operations remain.

The module writes JSON config with name, pool, container, block count, block size, and UUID. Resize opens the bdev, verifies it belongs to this module, rejects shrinking, obtains a DAOS channel, calls `dfs_punch()` from the new size to `DFS_MAX_FSIZE`, releases the channel, and notifies SPDK of the new block count. Deletion uses `spdk_bdev_unregister_by_name()`. DAOS error conversion is implemented locally because the referenced DAOS helper is not exported by DAOS packages.
