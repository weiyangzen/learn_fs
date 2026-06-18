<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.hh

Purpose: Defines the public plugin contract for translating logical, physical, and remote file names in XRootD storage paths.

APIs and control flow: `XrdOucName2Name` declares pure virtual `lfn2pfn()`, `lfn2rfn()`, and `pfn2lfn()`. `XrdOucName2NameVec` declares `n2nVec()` and provides `Recycle()` for vectors of heap strings. `XrdOucgetName2NameArgs` standardizes plugin factory arguments, and the extern "C" `XrdOucgetName2Name()` entry point is the loader ABI.

State and persistence: The header defines interfaces only. Implementations decide mapping state; returned vector contents are heap-owned until `Recycle()`.

Dependencies and integration: Used by default OSS, statlib users, `XrdOucN2NLoader`, external namelib plugins, and substitution helpers.

Risks and test signals: The comments emphasize efficiency because translation is on hot metadata paths. ABI tests should compile external plugins, verify extern "C" symbol visibility, version metadata guidance, vector recycling, and errno-style return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucName2Name.hh -->
