# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceSparseImage.h

This header declares `DeviceSparseImage`, a `Device` implementation for `.sparseimage` files.

It stores a vector mapping logical bands to physical file offsets, logical image size, band size, and the underlying `DiskImageFile`.

Public methods implement the standard device API.

The adapter is read-only and sparse-aware, returning zeroes for unallocated bands.
