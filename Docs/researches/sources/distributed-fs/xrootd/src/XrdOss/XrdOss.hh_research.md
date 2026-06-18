# sources/distributed-fs/xrootd/src/XrdOss/XrdOss.hh

## Purpose

`XrdOss.hh` defines the public XRootD object storage system plugin interface. It specifies per-file/directory object operations (`XrdOssDF`), filesystem-wide operations (`XrdOss`), option/feature flags, plugin entry-point typedefs, and default name-to-name helpers.

## Important APIs, Types, and Functions

`XrdOssDF` declares directory operations (`Opendir`, `Readdir`, `StatRet`), file operations (`Open`, `Clone`, `Fchmod`, `Fstat`, `Fsync`, `Ftruncate`, `getMmap`, `isCompressed`, read/write/async/page/vector methods), common `Close`, `Fctl`, `getErrMsg`, `getFD`, and `getTID`. `XrdOss` declares `newDir`, `newFile`, `Chmod`, `Connect`, `Create`, `Disc`, `EnvInfo`, `Features`, `FSctl`, `Init`, `Mkdir`, `Reloc`, `Remdir`, `Rename`, `Stat`, `Stats`, space/stat/xattr methods, `Truncate`, `Unlink`, and `Lfn2Pfn`. It defines flags such as `XRDOSS_mkpath`, `XRDOSS_new`, `XRDOSS_Online`, feature bits like `XRDOSS_HASPGRW`, and plugin typedefs `XrdOssGetStorageSystem_t`, `XrdOssGetStorageSystem2_t`, and `XrdOssAddStorageSystem2_t`.

## Control Flow

This header contains mostly virtual contracts and inline defaults. Runtime flow is selected by OFS calling into an `XrdOss` instance, obtaining `XrdOssDF` objects, and then invoking directory/file operations through virtual dispatch.

## State and Persistence Behavior

`XrdOssDF` stores trace identity, page-write EOF tracking, file descriptor, and type flags. `XrdOss` itself has no base storage. Concrete implementations decide persistence. Plugin entry points may wrap or replace the native implementation.

## Dependencies and Integration Points

The interface depends on POSIX stat/types, `XrdOssVS`, `XrdOucIOVec`, `XrdOucRange`, and forward-declared OUC/SFS/Sys types. It is the ABI-like boundary for external OSS plugins, default OSS implementation, OFS, proxy/cache layers, and storage wrappers.

## Risks and Edge Cases

This header is a compatibility boundary: changing virtual method order, signatures, flags, or object layout can break plugins. Several defaults return directory/file mismatch errors, so derived classes must override the right methods for their declared `DFType`. Public plugin typedef comments strongly imply version metadata should accompany plugins.

## Test Signals

ABI-sensitive tests include plugin compile/load tests, default method behavior, feature-bit discovery, `Lfn2Pfn` V1/V2 compatibility, file descriptor ownership, async/page capability negotiation, and wrapper plugin stacking.
