# File Research: sources/virtualization/libguestfs/daemon/copy.c

Implements in-process byte-copy APIs for file/device combinations.

Key points:
- Shared `copy` helper handles source/destination opening, optional source offset, destination offset, size limit, sparse-hole creation, and progress.
- Negative offsets and sizes are rejected when specified.
- Sparse mode seeks over all-zero buffers instead of writing them.
- Unlimited-size copies use pulse-mode progress; fixed-size copies report position/total.
- Supports device-to-device, device-to-file, file-to-device, and file-to-file.
- File destinations can append or truncate; append is rejected for device destinations.
- File-to-file deletes the destination on failure to avoid leaving partial created files.
