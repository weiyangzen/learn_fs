# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPages.cc

Purpose: implements the page-level checksum manager for the CSI plugin. It opens tag storage, tracks data/tag lengths, verifies reads, stores checksums for writes, supports pgRead/pgWrite checksum vectors, truncates tag state, and performs loose-write consistency repair.

Important APIs/functions: `Open()` opens tagstore and optionally allows missing tags. `TrackedSizesGet()`, `LockSetTrackedSize()`, `LockResetSizes()`, and `TrackedSizeRelease()` serialize tag/data length updates. `UpdateRange()` and `StoreRange()` update tag checksums before data writes, dispatching aligned or unaligned helpers. `VerifyRange()` and `FetchRange()` validate or return checksums after data reads. `apply_sequential_aligned_modify()` batches tag writes. `LockTrackinglen()` coordinates range locks through `XrdOssCsiRanges`. `truncate()` adjusts tag state and verifies partial pages. `pgDoCalc()` and `pgWritePrelockCheck()` support page checksum protocol. `BasicConsistencyCheck()` repairs some tag/data length mismatches in loose-write mode.

State/persistence: persistent metadata is in `XrdOssCsiTagstore`; in-memory state tracks missing tags, readonly, loose-write mode, update locks, range locks, and last-page checks. Data and tag sizes may intentionally differ after crashes or failures until repaired.

Risks/test signals: correctness depends on aligned/unaligned dispatch, range lock release on every error path, checksum convention consistency, missing-tag policy, and update-before-data-write failure recovery. Tests should cover empty/missing tag files, reads past tracked length, partial final pages, extension holes, truncation both directions, pgWrite verify/doCalc modes, loose-write repairs, and concurrent overlapping ranges.
