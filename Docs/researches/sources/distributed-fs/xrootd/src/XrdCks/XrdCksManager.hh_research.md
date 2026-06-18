# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.hh

Purpose: declares `XrdCksManager`, the base checksum manager implementation and extensibility point for filesystem-specific managers. Public methods implement the `XrdCks` contract for calculating, configuring, deleting, getting, listing, setting, sizing, naming, and verifying checksum values.

Important APIs/types: virtual public manager methods, `Cks_nomtchk` option, protected `Calc(Pfn, MTime, CksObj)` and `ModTime()` hooks, and private `csInfo` with name, calculator object, plugin path/parameters, plugin handle, checksum length, and ownership flag.

Control flow/state: the class maintains a fixed-size registry of checksum implementations and optionally owns an `XrdCksLoader` for autoload. Subclasses can override the protected methods to adapt file reads and stat calls while retaining xattr persistence and algorithm handling. Dependencies are `XrdCks`, `XrdCksData`, `XrdCksCalc`, plugin/version/error types. Risks include raw ownership, registry size limit, and the need for subclasses to preserve base expectations around PFN identity and mtime. Test signals: subclass override behavior, option propagation, algorithm registry bounds, and lifecycle cleanup.
