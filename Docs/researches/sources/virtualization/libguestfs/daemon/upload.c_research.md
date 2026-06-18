# File Research: sources/virtualization/libguestfs/daemon/upload.c

## Role
Implements raw file/device upload and download actions over the libguestfs FileIn/FileOut protocol.

## Upload Path
- `upload_to_fd()` receives FileIn chunks and writes them to a supplied file descriptor, tracking progress.
- `upload()` opens either a device path directly or a guest filesystem path under chroot, optionally seeks to an offset, and delegates to `upload_to_fd()`.
- `do_upload()` truncates or creates the target.
- `do_upload_offset()` writes at an offset without truncation and rejects negative offsets.

## Download Path
- `do_download()` opens a file or device, rejects directories, computes total size, replies, and streams chunks.
- Device sizes are obtained through `do_blockdev_getsize64()`.
- `do_download_offset()` streams a bounded range from a file/device and permits short reads at EOF.

## Protocol Semantics
After the initial FileOut reply, later read/close errors cannot be reported as normal RPC errors; the transfer is canceled instead.

## Filesystem/Storage Relevance
This is the low-level data transfer path for moving whole files or block-device contents between host and guest.
