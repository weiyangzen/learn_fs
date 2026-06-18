# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/devcache_impl.h

This private implementation header defines the on-disk packed nvlist file header and in-kernel descriptors for `/etc/devices` cache persistence.

The file format header uses magic `NVPF_HDR_MAGIC`, version `NVPF_HDR_VERSION`, fixed header size `NVPF_HDR_SIZE`, and `nvpf_hdr_t` with size, header checksum, and payload checksum fields plus padding for future extension.

Kernel-only `kfile_t` wraps vnode-based kernel file I/O state: vnode pointer, flags, filename, file position, and state. `nvfd_t`/`struct nvfiledesc` is the registered cache file descriptor, storing client ops, state flags, data list, rwlock, and global list linkage.

`NVF_F_*` flags track dirty, flushing, error, read-only, create-message, and rebuild-message states. Helper macros test/mark/clear dirty state and mark read-only state. Shorthand macros access the client ops vector.

The file declares `kfio_report_error`, defines temporary filename suffix constants, and debug macros for the nvpacked daemon and kernel file I/O under `DEBUG`.

Research notes:
- File header format is persistent and should be treated as ABI for existing `/etc/devices` cache files.
- The dirty/flushing/read-only flags coordinate asynchronous flush behavior.
- This header depends on `nvf_ops_t` from `devcache.h`.
