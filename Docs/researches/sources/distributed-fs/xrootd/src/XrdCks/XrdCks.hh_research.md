# sources/distributed-fs/xrootd/src/XrdCks/XrdCks.hh

Purpose: defines the abstract checksum manager interface used by XRootD and checksum plugins.

Important APIs and types: `XrdCksPCB` provides progress callback `Info(fsize, csbytes)`. `XrdCks` declares pure virtual methods `Calc`, `Del`, `Get`, `Config`, `Init`, `List`, `Name`, `Object`, `Size`, `Set`, and `Ver`, with overloads accepting a progress callback. The header also defines `XRDCKSINITPARMS` and documents the external `XrdCksInit()` plugin entry point and version-info convention.

Control flow and integration: managers may compute checksums, persist them in xattrs, retrieve and validate them, or delegate to plugin calculators. The interface supports both physical and logical filenames depending on manager configuration and OSS integration.

State and persistence: base class stores `XrdSysError *eDest` for diagnostics. Persistent checksum values are managed by concrete implementations, often in extended attributes.

Dependencies: includes `XrdCksData.hh` and forward-declares stream, plugin, and error classes.

Risks and test signals: implementation tests should verify negative errno contracts (`-EDOM`, `-ENOTSUP`, `-ESRCH`, `-ESTALE`), default checksum selection, progress callback invocation, and logical/physical filename routing with OSS-backed managers.
