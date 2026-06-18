# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32.hh

Purpose: declares and partly implements the built-in CRC-32 checksum calculator.

Important APIs: `Init()` resets `C32Result` and `TotLen`. `Update()` is implemented in the `.cc`. `Final()` appends the encoded total length to the CRC calculation, xors with `CRC32_XOROT`, converts to network order on little-endian platforms, and returns a pointer to `TheResult`. `Type()` returns `"crc32"` and 4-byte size.

Control flow and integration: designed for incremental manager-driven updates. `New()` creates a fresh calculator for loader/manager use.

State and persistence: stores the static table, current CRC, final result, and total bytes processed. Persistent representation is only the final binary checksum.

Dependencies: includes `XrdCksCalc.hh`, platform/endian support, and byte-order headers.

Risks and test signals: test vectors must account for XRootD's length-finalization behavior rather than generic reflected CRC-32. Tests should verify endian output and repeated reuse after `Init()`.
