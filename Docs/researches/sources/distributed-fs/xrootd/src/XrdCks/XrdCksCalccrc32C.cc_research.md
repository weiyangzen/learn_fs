# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.cc

Purpose: implements the CRC-32C checksum calculator using `XrdOucCRC::Calc32C`.

Important APIs: `Update()` feeds each buffer into `Calc32C` with the current CRC seed. `Type()` returns `"crc32c"` and 4-byte size. `New()`, `Init()`, `Final()`, constructor, and destructor provide the standard `XrdCksCalc` lifecycle.

Control flow: the calculator keeps an accumulated CRC in `C32CResult`; `Final()` returns it as `TheResult`, converted to network order on little-endian platforms.

State and persistence: transient calculator state only. Final bytes may be stored in `XrdCksData`.

Dependencies: includes `XrdCksCalccrc32C.hh`, which pulls in `XrdOucCRC`.

Risks and test signals: tests should compare known CRC-32C vectors, segmented versus one-shot updates, endian conversion, and object reuse. Because no length finalization is applied, vectors differ from `XrdCksCalccrc32`.
