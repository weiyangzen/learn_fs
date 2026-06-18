# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.cc

Purpose: implements an OSS-backed checksum manager adapter. It converts logical file names to physical file names through `XrdOss::Lfn2Pfn`, then delegates most checksum metadata operations to `XrdCksManager`, while overriding file reads and stat calls to use the OSS file interface.

Important APIs: public `Calc`, `Del`, `Get`, `List`, `Set`, `Ver`; protected `Calc(Pfn, MTime, XrdCksCalc*)` and `ModTime`. `LfnPfn` stores the original LFN immediately before the PFN buffer, allowing `Pfn2Lfn()` to recover the logical name when base-class callbacks pass the PFN pointer back.

Control flow/state: a namespace-global `ossP` points to the active OSS instance and `rdSz` is normalized to a 64 KiB multiple. `Calc` opens through `ossP->newFile`, verifies a regular file, reads chunks into a heap buffer, updates the calculator, and reports read errors through `XrdSysError`. Persistence remains xattr-based in the base manager. Risks: global `ossP`, pointer-layout coupling in `Pfn2Lfn`, and large-buffer allocation. Test signals: failed LFN conversion, non-regular object, read failure, successful Set/Get via OSS.
