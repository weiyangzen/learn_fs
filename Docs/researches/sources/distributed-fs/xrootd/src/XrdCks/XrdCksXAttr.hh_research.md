# sources/distributed-fs/xrootd/src/XrdCks/XrdCksXAttr.hh

Purpose: defines the xattr payload adapter used by `XrdOucXAttr` to persist `XrdCksData` under algorithm-specific extended attribute names.

Important APIs/types: public `Cks` member, `postGet(Result)`, `preSet(tmp)`, `Name()`, `sizeGet()`, and `sizeSet()`. `Name()` builds `"XrdCks." + Cks.Name`; sizes are exactly `sizeof(Cks)`.

Control flow/state: `preSet` copies checksum data into a temporary object and converts `fmTime`/`csTime` to network byte order; `postGet` converts those fields back to host order after successful reads. The generated attribute name is cached in `VarName` until object mutation. Persistence is the filesystem extended attribute keyed by algorithm name. Dependencies are `XrdCksData`, endian conversion helpers, and platform definitions. Risks: cached name becomes stale if `Cks.Name` changes after `Name()` is called, binary struct compatibility, and architecture portability limited to converted time fields. Test signals: set/get round trip across byte order, multiple checksum names, and xattr name construction.
