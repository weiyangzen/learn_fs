# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalczcrc32.cc

Purpose: implements a loadable zlib-compatible CRC32 calculator plugin named `zcrc32`.

Important APIs: class `XrdCksCalczcrc32 : public XrdCksCalc` implements `Init()` with `crc32(0L, Z_NULL, 0)`, `Update()` with zlib `crc32`, `Final()` returning the current `uint32_t`, `New()`, and `Type()` returning `"zcrc32"` with 4-byte size. The extern "C" `XrdCksCalcInit()` factory returns a new calculator, and `XrdVERSIONINFO` declares plugin version metadata.

Control flow and integration: built as a module by `XrdCks/CMakeLists.txt` and loaded by the checksum loader when configured. It provides zlib semantics separately from XRootD's built-in CRC32 algorithm.

State and persistence: `pCheckSum` is per-instance transient state. Final bytes may be stored by a checksum manager.

Dependencies: depends on zlib, `XrdCksCalc.hh`, `XrdSysError.hh`, and `XrdVersion.hh`.

Risks and test signals: plugin load tests should validate the factory symbol and version info. Algorithm tests should compare standard zlib CRC32 vectors, incremental updates, and byte-order expectations of consumers.
