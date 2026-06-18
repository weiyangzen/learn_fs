# sources/distributed-fs/xrootd/src/XrdCks/XrdCksCalccrc32C.hh

Purpose: declares the CRC-32C `XrdCksCalc` subclass.

Important APIs: declares `Final`, `Init`, `New`, `Update`, `Type`, constructor, and destructor. Private members are initial constant `C32C_XINIT`, current result, and final output word.

Control flow and integration: used as a built-in checksum calculator through the manager/loader stack, with the implementation delegating arithmetic to `XrdOucCRC::Calc32C`.

State and persistence: no persistent state beyond returned checksum bytes.

Dependencies: includes `XrdCksCalc.hh`, platform/endian headers, byte-order support, and `XrdOucCRC.hh`.

Risks and test signals: ABI and type-name tests should ensure `"crc32c"` is registered and reports the correct size. Algorithm tests should verify output byte order.
