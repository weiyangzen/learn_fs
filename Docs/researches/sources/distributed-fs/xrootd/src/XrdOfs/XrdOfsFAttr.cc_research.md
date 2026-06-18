# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsFAttr.cc

## Purpose

This file implements `XrdOfs::FAttr()` and the local extended-attribute control helpers. It exposes SFS file attribute operations for delete, get, list, and set, with authorization, redirect/proxy handling, export option checks, LFN-to-PFN conversion, and buffer management for attribute results.

## Important APIs, types, and functions

`FAttr()` is the entry point. Passing `faReq == nullptr` returns support metadata through the request environment. `ctlFADel()`, `ctlFAGet()`, `ctlFALst()`, and `ctlFASet()` implement local operations through `XrdSysFAttr::Xat`. Helper functions allocate response buffers (`GetFABuff()`), fetch values into packed buffers (`GetFAVal()`), retry oversized values (`GulpFAVal()`), and mark remaining attributes as `ENOMEM` (`SetNoMem()`).

## Control flow

`FAttr()` first handles support probing, validates request type, builds an `XrdOucEnv` from path CGI and client identity, obtains export options, and optionally performs authorization/remote location. Write requests are rejected for read-only exports. Proxy servers forward the whole request to OSS with `XRDOSS_FSCTLFA`; local servers reject no-xattr exports, translate the logical path to a physical path, and dispatch to the matching `ctlFA*` method.

List flow gets all xattr names, filters by prefix, optionally explodes names into `XrdSfsFAInfo`, optionally returns value sizes/values, and frees the xattr list. Get flow allocates an initial block and fetches each named attribute, growing by additional blocks for `ERANGE`. Set flow serializes replacement-style sets under `faMutex` but does not lock when creating new attributes.

## State and persistence behavior

The file itself keeps only a local mutex. Durable state is the filesystem xattr store behind `XrdSysFAttr::Xat`, addressed by PFN. Response buffers are attached to `faCtl.fabP` for the SFS caller to return/free according to interface expectations.

## Dependencies and integration points

It integrates with OFS authorization macros, `Finder` redirection, export option lookup, `XrdOfsOss` path mapping/proxy FSctl, `XrdSysFAttr`, `XrdSfsFACtl`, and XRootD security identity. It is the local implementation of attribute operations advertised through SFS.

## Risks and test signals

The prefix length calculation uses `sizeof(faCtl.nPfx)` when the prefix is non-empty, so behavior depends on `nPfx` being a fixed char array and may not mean string length. Buffer packing for list-with-values temporarily swaps `Name` and `Value`, which needs careful tests. Proxy and local paths have different execution surfaces. Tests should cover support probing, no-xattr/read-only export failures, remote locate failures, PFN mapping failures, list prefix filtering, large value fallback, per-attribute errors, new versus replace set locking, and proxied requests.
