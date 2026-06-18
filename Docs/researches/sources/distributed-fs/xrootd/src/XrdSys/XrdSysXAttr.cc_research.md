# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXAttr.cc

Purpose: provides default behavior shared by extended-attribute implementations: copying attributes between files and setting the message route.

Important APIs/types/functions: `XrdSysXAttr::Copy()` and `XrdSysXAttr::SetMsgRoute()` are implemented here; concrete plugins provide `Del()`, `Free()`, `Get()`, `List()`, and `Set()`.

Control flow: when no attribute name is supplied, `Copy()` calls `List(getSz=1)`, allocates a buffer larger than the reported maximum value size, loops over all returned attributes, gets each value, sets it on the output, frees the list, and returns the last status. For a single attribute, it first probes size via `Get(Aval=null, Avsz=0)`, allocates exactly that size, gets the value, sets it on the target, and treats `-ENOTSUP` as a successful no-op.

State and persistence: no persistent state besides the inherited `Say` pointer. Memory for copy buffers is temporary; `List()` ownership is released through the virtual `Free()`.

Dependencies and integration: includes `XrdSysError` and `XrdSysXAttr.hh`. The default copy routine works with native and plugin xattr backends.

Risks: in the all-attributes path, `malloc(maxSz)` is not checked before use. The loop passes `aNow->Vlen` to `Set()` even when `Get()` returned a different byte count. Missing or unsupported attributes are considered success, which is deliberate but may hide configuration mistakes.

Test signals: copy all attributes, copy one attribute, no xattr support, zero-length attributes, allocation failure injection, and plugin `List()`/`Free()` ownership correctness.
