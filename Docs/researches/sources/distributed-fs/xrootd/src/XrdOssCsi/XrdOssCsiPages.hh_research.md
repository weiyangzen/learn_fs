# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.hh

Purpose: declares the core page checksum manager used by `XrdOssCsiFile`. It exposes high-level range update/verify/fetch/store methods while hiding tagstore access, range locking, and aligned/unaligned page math.

Important APIs/types: `Sizes_t` is `(tag_tracked_size, data_tracked_size)`. Public methods include `Open`, `Close`, `UpdateRange`, `VerifyRange`, `FetchRange`, `StoreRange`, `LockTrackinglen`, `truncate`, `TrackedSizesGet`, `LockResetSizes`, `VerificationStatus`, `pgDoCalc`, and `pgWritePrelockCheck`. Protected helpers cover aligned and unaligned read/write paths, hole extension, pre/post partial blocks, full/max reads, and formatted diagnostics for CRC mismatches and tag/page IO errors.

State/control: owns `std::unique_ptr<XrdOssCsiTagstore>`, `XrdOssCsiRanges`, mutex/condition variables for tracking-size updates, booleans for missing tags/read-only/loose writes/config flags, file identity strings, and last-page loose-write state. `LockTrackinglen()` sets range guards that later release tracked-size update locks.

Dependencies/integration: depends on tagstore abstraction, range guard implementation, XRootD page size, and `XrdOssDF` operations. Risks include complex lock ownership between `TrackedSizesGet()` and range guards, reliance on external unaligned implementation file, and static stack buffers sized by `stsize_`. Tests should validate public methods across aligned, unaligned, missing-tag, readonly, and concurrent access paths.
