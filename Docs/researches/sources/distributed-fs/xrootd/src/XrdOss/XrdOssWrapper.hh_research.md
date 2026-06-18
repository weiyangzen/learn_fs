# sources/distributed-fs/xrootd/src/XrdOss/XrdOssWrapper.hh

Purpose: provides pass-through wrapper classes for OSS plug-ins that want to intercept selected `XrdOss`, `XrdOssDF`, directory, or file methods while delegating the rest to an underlying implementation.

Important APIs/types/functions: `XrdOssWrapDF` wraps `XrdOssDF` methods; `XrdOssWrapper` wraps top-level `XrdOss` methods. It forwards directory methods (`Opendir`, `Readdir`, `StatRet`), file methods (`Open`, `Read`, `Write`, vector I/O, page I/O, async I/O, clone, truncate, sync, mmap, compression), common close/error/Fctl methods, top-level namespace methods (`Create`, `Mkdir`, `Rename`, `Remdir`, `Unlink`, `Stat*`, `Truncate`, `Reloc`), lifecycle methods, and LFN-to-PFN translation.

Control flow: every method is inline and immediately calls the same method on `wrapDF` or `wrapPI`. Derived wrappers override only the operations they need; non-overridden operations preserve the underlying OSS behavior.

State and persistence behavior: the wrappers own no persistent state. They hold references to underlying objects; underlying operations perform all filesystem, cache, and remote side effects.

Dependencies: `XrdOss/XrdOss.hh` supplies the full interface and related types such as `XrdOucEnv`, `XrdSfsAio`, `XrdOucIOVec`, `XrdOssVSInfo`, and `XrdOucCloneSeg`.

Integration points: `XrdOssArc` uses this pattern to wrap an existing OSS and enforce archive behavior. Other pushed OSS plug-ins can stack wrappers without reimplementing the complete interface.

Risks: wrapper lifetimes are reference-based; the creator remains responsible for deleting underlying objects. Missing an override means behavior silently passes through. Inline forwarding can hide ownership semantics for `newDir/newFile`, `resp` buffers, and error-message thread locality.

Test signals: derive a wrapper that intercepts one method and verify all other methods pass through, destructor/lifetime tests for wrapped DF objects, error-message propagation, and API coverage after adding new `XrdOss` virtual methods.
