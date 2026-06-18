# File Research: sources/virtualization/qemu/block/vmdk.c

QEMU block format driver for VMware VMDK images. It supports descriptor-based VMDKs, monolithic sparse, flat and split extents, VMFS sparse, streamOptimized compressed images, zeroed-grain sparse images, and read-only seSparse extents.

Key responsibilities:
- Detect VMDK images via VMDK3/VMDK4 magic or descriptor `version=` lines.
- Parse descriptor files, `createType`, extent lines, parent hints, CID and parent CID fields.
- Open and manage multiple ordered `VmdkExtent` objects, each with its own child file, L1/L2 tables, cluster geometry, compression flags, and flat/sparse/seSparse mode.
- Validate backing image CID before reading or copying from the parent.
- Implement cluster lookup and allocation through L1/L2 grain tables, including L2 cache management and zeroed-grain handling.
- Implement COW allocation through `get_whole_cluster()`, preserving backing data outside the written byte range.
- Support zlib-compressed streamOptimized grain reads/writes with `VmdkGrainMarker`.
- Create VMDK images and extents for monolithic/split, flat/sparse, streamOptimized, backing-file, compat6, hwversion, toolsVersion, and zeroed-grain options.
- Report block status, allocated file size, zero initialization, driver-specific image info, and block driver info.
- Register the `vmdk` format `BlockDriver`.

Important structures:
- `VMDK3Header`, `VMDK4Header`: on-disk sparse headers.
- `VMDKSESparseConstHeader`, `VMDKSESparseVolatileHeader`: seSparse header validation structures.
- `VmdkExtent`: per-extent state, child file, table offsets, cache, geometry, flags.
- `BDRVVmdkState`: whole-image state, extent array, CID state, migration blocker, create type.
- `VmdkMetaData`: L1/L2 indices used when updating an allocation.
- `VmdkGrainMarker`: compressed stream grain header.

Core flow:
- `vmdk_open()` opens the primary child, reads either sparse header or text descriptor, parses extents, opens parent hints, reads CIDs, initializes locking, and installs a migration blocker.
- Sparse opens go through `vmdk_open_vmfs_sparse()`, `vmdk_open_vmdk4()`, or `vmdk_open_se_sparse()`.
- I/O uses `find_extent()` plus `get_cluster_offset()` to map guest offsets to extent offsets. Reads fall back to backing or zeroes. Writes allocate clusters, perform COW, write data, update L2 tables, and update CID on first write.
- Creation is centralized in `vmdk_co_do_create()` with callback-based extent provisioning for legacy option creation and QAPI blockdev creation.

Notable constraints and risks:
- seSparse is opened read-only; dirty journal replay is explicitly unsupported.
- VMDK disables live migration through a migration blocker.
- StreamOptimized writes only allow whole-cluster compressed writes and reject rewrites to allocated compressed clusters.
- Descriptor parsing uses fixed-size buffers and explicit validation for extent syntax, paths, and supported types.
- L1 size, cluster size, sector limits, footer validity, VMDK version, and table sizes are guarded to reject corrupt images.
