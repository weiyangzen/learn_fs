# sources/distributed-fs/xrootd/src/XrdOss/XrdOssVS.hh

Purpose: declares virtual-space result structures returned by `XrdOss::StatVS`.

Important APIs/types/functions: `XrdOssVSPart`, `XrdOssVSInfo`, and `XrdOssVSInfo::Export`.

Control flow: no runtime logic beyond constructors, destructor, and `Export()`. `Export()` transfers ownership of `vsPart` out of `XrdOssVSInfo`, clears the member, and returns the partition count.

State and persistence behavior: purely transient query result state. `XrdOssVSPart` describes a partition path, allocation paths, total/free bytes, block-device id, and partition id. `XrdOssVSInfo` aggregates totals, largest/free extents, usage, quota, extent count, and optional partition vector.

Dependencies: none beyond C++ core types. Populated by OSS cache/stat code.

Integration points: used by `XrdOssSys::StatVS` and consumers that need space totals or partition placement information for scheduling and monitoring.

Risks: ownership of `pPath` and `aPath` is not described by constructors; callers must delete only the exported `vsPart` array and not inner pointers unless documented elsewhere. Device identifiers may be zero or ambiguous on non-Linux/software filesystems.

Test signals: aggregate-only `StatVS`, `+space` partition-vector queries, `Export()` ownership transfer, destructor cleanup, and platform-specific bdev/part id reporting.
