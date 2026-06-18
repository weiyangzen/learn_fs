# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcDir.hh

Purpose: declares `XrdOssArcDir`, the archive directory/file wrapper returned for directory operations.

Important APIs/types/functions: overrides `Close`, `getErrMsg`, and `Opendir`; constructor accepts trace id and underlying `XrdOssDF*`; private members `ossDF` and `zFile`.

Control flow: methods not overridden are inherited from `XrdOssWrapDF` and pass through to the underlying object. The constructor initializes the base wrapper with `*df` and stores `df` for ownership.

State and persistence behavior: owns and deletes the underlying DF object and optional zip-file adapter.

Dependencies: `XrdOssWrapper.hh`, forward declarations for `XrdOssArcZipFile`, `XrdOucEnv`, and `stat`.

Integration points: created by `XrdOssArc::newDir`; works with compose and zip modules to expose archives through OSS directory APIs.

Risks: constructor dereferences `df` immediately, so null underlying objects crash; ownership is implicit and differs from base reference semantics; most methods still pass through and may not be archive-safe unless intercepted elsewhere.

Test signals: null-underlying defensive tests, destructor ownership, pass-through inherited methods, and overridden close/open/error paths.
