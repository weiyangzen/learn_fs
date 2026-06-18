# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/mds_export.c

This file implements pNFS metadata-server export/module operations for SaunaFS. It reports supported layouts, estimates XDR buffer sizes, and converts SaunaFS chunk/chunkserver topology into NFSv4.1 file-layout device information.

Important helpers are `randomizedChunkserverList`, `fillChunkDataServerList`, `fillUnusedDataServerList`, `releaseResources`, `getdeviceinfo`, `getdevicelist`, `fs_layouttypes`, `fs_layout_blocksize`, `fs_maximum_segments`, `fs_loc_body_size`, `fs_da_addr_size`, `exportOperationsPnfs`, and `pnfsMdsOperationsInit`. It filters disconnected chunkservers, removes duplicate IPs after sorting, randomizes usable servers, and encodes multipath data-server addresses with `FSAL_encode_v4_multipath`.

Control flow for `getdeviceinfo` validates `LAYOUT4_NFSV4_1_FILES`, finds the export by `deviceid->device_id2`, retrieves chunk info for `deviceid->devid`, builds a randomized chunkserver list, computes a stripe count bounded by `SAUNAFS_BIGGEST_STRIPE_COUNT`, encodes stripe indices, encodes chunk-local DS lists first, fills remaining stripes from randomized servers, and frees SaunaFS-allocated chunk metadata. `getdevicelist` returns EOF without entries; layouts rely on encoded device IDs from layoutget.

State is not stored persistently here. It derives layout/device answers from current SaunaFS chunkserver and chunk metadata. Randomization uses `srandom(time(NULL))` per shuffle call.

Dependencies include `pnfs_utils`, XDR helpers, SaunaFS chunk APIs, and FSAL module export lists. Risks include a suspicious `remove_if` copy direction that appears to copy from `step` to `i` rather than keeping element `i` at `step`, random seeding per request, no device list enumeration, fixed NFS port/protocol assumptions, and large XDR sizing. Test signals should cover disconnected/duplicate chunkservers, chunks with standard and nonstandard parts, no chunkservers, large files near stripe limits, device export lookup failure, and XDR encode failures.
