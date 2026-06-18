# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiCrcUtils.cc

Purpose: defines the static zero-filled page buffer used by CRC utility routines. The implementation file contains only `XrdOssCsiCrcUtils::g_bz[XrdSys::PageSize] = {0}`.

Important APIs/state: the buffer supports zero-extension, split, and combine operations in the header. It is sized to the XRootD system page size, matching the plugin's checksum granularity.

Dependencies/integration: includes `XrdOssCsiCrcUtils.hh`, which in turn depends on `XrdOucCRC` and `XrdSysPageSize`. This file must be linked into the plugin exactly once to satisfy the static member definition.

Risks/test signals: risk is low but build-sensitive; omitting this source would produce unresolved symbols, while multiple definitions would break linkage. Runtime tests should indirectly verify zero-fill CRC operations through page extension and unaligned writes. Unit-level checks can compare `crc32c_extendwith_zero()` against direct `Calc32C` over explicit zero bytes.
