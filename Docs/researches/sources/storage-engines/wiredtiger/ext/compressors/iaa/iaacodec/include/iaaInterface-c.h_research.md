
## sources/storage-engines/wiredtiger/ext/compressors/iaa/iaacodec/include/iaaInterface-c.h

Purpose: provides the C ABI for the C compressor adapter to call the C++ IAA codec without exposing C++ symbols or types beyond WiredTiger pointers.

Important APIs: `getMaxCompressedDataSize`, `doCompressData`, and `doDecompressData` are declared in an `extern "C"` block when compiled under C++. They accept `WT_COMPRESSOR *`, `WT_SESSION *`, raw byte buffers, `uint32_t` sizes, and an optional decompression result pointer.

Control flow and state: this header has no state, but its ABI enforces the 32-bit length contract used by both the C adapter and C++ codec. Integration points are `iaa_compress.c` and `iaaInterface-c.cpp`. Risks are ABI drift, C/C++ include compatibility, and truncation if callers pass sizes wider than `uint32_t`. Test signals are compile/link tests from C and C++, plus compressor round trips through the exported C functions.
