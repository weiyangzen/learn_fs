# File Research: sources/os/linux/linux/fs/cachefiles/Kconfig

## Purpose
Defines build-time configuration for CacheFiles, the FS-Cache backend that uses a mounted local filesystem as persistent cache storage.

## Main Elements
- `CACHEFILES`: tristate option depending on `NETFS_SUPPORT`, `FSCACHE`, and `BLOCK`.
- `CACHEFILES_DEBUG`: optional dynamic debug mask support through the module parameter.
- `CACHEFILES_ERROR_INJECTION`: optional sysctl-controlled fault injection support.
- `CACHEFILES_ONDEMAND`: optional on-demand read mode where userspace supplies cache-miss data through the CacheFiles daemon interface.

## Dependencies And Integration
Connects CacheFiles to the kernel netfs/FS-Cache infrastructure and block-backed filesystems. The help text points to `Documentation/filesystems/caching/cachefiles.rst`.

## Risk Notes
On-demand mode changes the data-fetching responsibility from the netfs to userspace and is disabled by default. Error injection requires `SYSCTL` and is intended for testing active caches.
