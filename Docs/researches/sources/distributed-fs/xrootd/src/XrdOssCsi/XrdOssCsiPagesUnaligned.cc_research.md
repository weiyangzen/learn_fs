# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiPagesUnaligned.cc

## Purpose
Implements the unaligned read/write checksum paths for `XrdOssCsiPages`. It maintains per-page CRC32C tags when writes do not align cleanly to `XrdSys::PageSize`, when writes extend a file through sparse holes, or when reads need verification/checksum results for partial pages.

## Important APIs and control flow
`UpdateRangeHoleUntilPage()` fills missing tag entries between the tracked file size and a later page, extending a partial tracked page with zero CRC state and then writing either zero-filled-page CRCs or literal zero tags depending on `writeHoles_`. `UpdateRangeUnaligned()` is a wrapper around `StoreRangeUnaligned()` for ordinary writes without a caller-provided checksum vector.

`StoreRangeUnaligned()` handles partial first pages via `StoreRangeUnaligned_preblock()`, optional partial final pages via `StoreRangeUnaligned_postblock()`, and delegates full interior tag updates to `apply_sequential_aligned_modify()`. The preblock path covers sparse append, append inside the current last page, and partial overwrite. Non-loose mode requires existing data to match the stored tag before recalculating; `loosewrite_` allows several recovery checks where on-disk content or an already-applied write can explain a mismatch.

`FetchRangeUnaligned()` reads the needed tags into either the caller's `csvec` or an internal tag buffer, verifies full pages in batches, and calls pre/post helpers to handle partial page verification and checksum-vector trimming.

## State, dependencies, and integration
State is the sidecar tagstore `ts_`, file name `fn_`, loose-write fields, and the tracked sizes supplied by the caller. It depends on `XrdOssDF` reads, `XrdOucCRC::Calc32C`, `XrdOssCsiCrcUtils` checksum combine/split helpers, `XrdSys::PageSize`, and CSI trace macros.

## Risks and test signals
Important risks are off-by-one page boundaries, signed/unsigned offset conversions, sparse-hole semantics when `writeHoles_` is false, and concurrent modification between user buffers and rereads. Good tests write and read ranges crossing page boundaries, append after holes, truncate and rewrite short last pages, exercise `Verify` plus `csvec`, and force corrupted tag/data mismatches in both strict and loose-write modes.
