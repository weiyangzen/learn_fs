# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssHandler.hh

## Purpose
Provides chain-of-responsibility base wrappers for OSS plugins. Derived classes can override selected methods while forwarding the rest to a successor OSS or data-file object.

## Important APIs and types
`XrdOssDFHandler` inherits `XrdOssDF` and forwards directory operations, file operations, page read/write operations, AIO methods, vector I/O, raw reads, close, fctl, and transaction ID access to `successor_`. Its constructor mirrors the successor's TID, DF type, and FD into the base class, and its destructor deletes the successor.

`XrdOssHandler` inherits `XrdOss` and forwards filesystem-level methods including chmod, connect/disconnect, create, features, fsctl, mkdir, reloc, remdir, rename, stat variants, truncate, unlink, and LFN/PFN translation. Comments indicate derived classes must provide `newDir()`, `newFile()`, and initialization behavior.

## State, dependencies, and integration
State is just the successor pointer. The header depends on `XrdOss.hh` and integrates with plugins that layer functionality such as CSI checksum validation or stats collection over an existing OSS.

## Risks and test signals
Ownership differs between classes: `XrdOssDFHandler` deletes its successor, while `XrdOssHandler` leaves its successor alive. Plugin tests should confirm ownership expectations, forwarding of all overloaded methods, and correct behavior when derived wrappers override only a subset of calls.
