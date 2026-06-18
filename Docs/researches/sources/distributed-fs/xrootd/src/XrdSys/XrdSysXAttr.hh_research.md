# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.hh

Purpose: defines the abstract extended-attribute interface used by XRootD native and plugin xattr providers.

Important APIs/types/functions: `XrdSysXAttr::AList` describes linked attribute names and value lengths. Virtual API includes default `Copy()`, pure `Del()`, `Free()`, `Get()`, `List()`, `Set()`, and default `SetMsgRoute()`. Factory typedefs are `XrdSysGetXAttrObject_t` and `XrdSysAddXAttrObject_t`.

Control flow: consumers call `List()` to enumerate, `Get()`/`Set()`/`Del()` to operate on one attribute, and `Copy()` to copy one or all attributes. Plugins can be loaded via `ofs.xattrlib`; add-style plugins can wrap an existing active implementation.

State and persistence: each implementation may store backend state; base class stores only `XrdSysError *Say`. `AList` allocations are implementation-owned and must be released by `Free()`.

Dependencies and integration: forward-declares `XrdOucEnv` and `XrdSysError`. The header documents expected extern C factory symbols and version declaration with `XrdVERSIONINFO`.

Risks: `AList` uses a flexible-array-style `Name[1]`, so implementations must allocate enough storage and preserve alignment. API returns negative errno values, not positive errno. File descriptors are optional and implementations must correctly choose fd-based or path-based syscalls.

Test signals: plugin load/factory ABI, list/free memory checks, fd and path variants, binary attribute values, `isNew` semantics, unsupported filesystem behavior, and wrapper plugin chaining.
