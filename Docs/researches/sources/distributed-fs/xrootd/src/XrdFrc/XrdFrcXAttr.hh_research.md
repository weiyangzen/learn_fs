<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXAttr.hh

## Purpose
`XrdFrcXAttr.hh` defines the extended attribute payloads used by FRM to track file residency metadata: copy time, memory mapping behavior, pinning, and PFN back-references. The classes are designed for use with the templated `XrdOucXAttr<T>` wrapper.

## Important Types
`XrdFrcXAttrCpy` stores `cpyTime` under `XrdFrm.Cpy` and converts the 64-bit value between host and network byte order. `XrdFrcXAttrMem` stores `Flags` under `XrdFrm.Mem`; flags request mmap, keep mapping, or memory lock. `XrdFrcXAttrPin` stores `pinTime` plus flags under `XrdFrm.Pin`; flags represent permanent, idle-duration, or until-time pins. `XrdFrcXAttrPfn` stores a null-terminated PFN string under `XrdFrm.Pfn` for cross-reference repair in extended-attribute cache layouts.

## Control Flow, State, And Persistence
Each class supplies the `Name()`, `sizeGet()`, `sizeSet()`, `postGet()`, and `preSet()` protocol expected by `XrdOucXAttr`. The persistent state is stored in filesystem xattrs and is portable for 64-bit time fields by network byte order conversion. `XrdFrcXAttrPfn::sizeSet()` persists only the string length plus terminator, not the full fixed buffer.

## Dependencies And Integration Points
The header depends on network byte-order helpers from `XrdSysPlatform.hh`, POSIX path sizes, and `<cstring>`. `XrdFrmAdminFiles`, `XrdFrmAdminAudit`, `XrdFrmAdminFind`, and `XrdFrcUtils::updtCpy()` use these payloads to set, read, list, repair, and delete metadata.

## Risks And Test Signals
`XrdFrcXAttrPin::sizeGet()` and `sizeSet()` return `sizeof(XrdFrcXAttrCpy)` rather than `sizeof(XrdFrcXAttrPin)`. That is a high-risk ABI bug unless intentionally relying on older oversized storage; it can cause reads/writes larger than the pin structure. `XrdFrcXAttrMem::preSet()` ignores its temp object and returns `this`, which is fine only because no byte-order conversion is needed. Tests should verify exact xattr sizes, round-trip byte order across simulated endian boundaries, expired pin deletion, PFN string truncation behavior, and compatibility with existing on-disk xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXAttr.hh -->
