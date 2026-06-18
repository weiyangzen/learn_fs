# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.cc

Purpose: contains the lookup table and streaming update routine for XRootD's built-in non-reflected CRC-32 calculator.

Important APIs: defines static `XrdCksCalccrc32::crctable[256]` and implements `Update(const char*, int)`, which increments total length and updates `C32Result` byte by byte with a table lookup based on the high byte of the current CRC and input byte.

Control flow: `Final()` in the header later folds total-length bytes into the CRC before xor/output conversion. This source only handles incremental data ingestion.

State and persistence: mutates the calculator instance fields `TotLen` and `C32Result`; final binary checksum may be persisted through manager/xattr layers.

Dependencies: includes `XrdCksCalccrc32.hh`.

Risks and test signals: tests should compare against established XRootD CRC32 vectors, verify segmented updates equal one-shot calculation, and exercise zero-length data because length folding happens in `Final()`.
