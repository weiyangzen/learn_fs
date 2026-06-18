## sources/distributed-fs/xrootd/src/XrdSys/XrdSysFAttr.cc

Purpose: selects and implements the native extended-file-attribute adapter and plugin hook.

Important APIs/types/functions: process-global `XrdSysXAttrNative` references default `dfltXAttr`; `XrdSysXAttrActive` and `XrdSysFAttr::Xat` point to the active attribute processor. Platform `.icc` files implement `Del`, `List`, `Get`, and `Set`; unsupported platforms return `-ENOTSUP`. Common helpers include `Diagnose()`, `Free()`, `getEnt()`, and `SetPlugin()`.

Control flow: compile-time platform selection includes BSD, Linux/GNU, macOS, or Solaris implementations. `Diagnose()` suppresses common missing-attribute/missing-path errors and logs other failures through `Say`. `getEnt()` optionally probes value size, allocates a variable-length `AList`, and links it at the head.

State and persistence: active implementation is global mutable state. `AList` nodes are heap-allocated with `malloc` and freed through `Free()`. Plugin replacement can delete the previous non-default implementation unless `push` is true.

Dependencies and integration: depends on `XrdSysXAttr.hh`, `XrdSysError.hh`, errno conventions, and platform xattr syscalls hidden in `.icc` files.

Risks: global active-plugin changes are unsynchronized. Ownership of plugin objects is subtle. Negative errno returns must be consistently interpreted by callers. `getEnt()` relies on dynamic struct sizing.

Test signals: platform xattr CRUD, missing attributes, unsupported platforms, plugin replacement/push behavior, `AList` list/free correctness, and diagnostics suppression versus emitted errors.
