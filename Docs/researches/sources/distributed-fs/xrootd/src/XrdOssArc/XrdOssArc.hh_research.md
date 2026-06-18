# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.hh

Purpose: declares `XrdOssArc`, the archive-aware `XrdOssWrapper` subclass.

Important APIs/types/functions: overrides `newDir`, `newFile`, mutation methods, `Features`, `FSctl`, `getErrMsg`, `Lfn2Pfn`, `Stat`, `Truncate`, `Unlink`, and `InitArc`. `newDir` returns `XrdOssArcDir`; `newFile` returns `XrdOssArcFile`.

Control flow: the header defines wrapper construction and factory overrides inline, with operational behavior implemented in `XrdOssArc.cc` and archive file behavior in companion files.

State and persistence behavior: owns no additional members beyond `XrdOssWrapper::wrapPI`; runtime state is global in the implementation and in returned dir/file wrappers.

Dependencies: `XrdOssWrapper.hh`, `XrdOssArcDir.hh`, `XrdOssArcFile.hh`, and `XrdOucEnv`.

Integration points: used by the plug-in entry point to present a complete OSS interface to OFS while routing archive paths to special dir/file wrappers.

Risks: `newDir/newFile` do not check whether `wrapPI.newDir/newFile` returned null before constructing wrappers, so allocation or underlying factory failure handling depends on wrapper constructors/usage. Adding new `XrdOss` virtual methods requires updating this wrapper if archive behavior should intercept them.

Test signals: factory creation with valid and null underlying objects, override coverage, compile against current `XrdOss` ABI, and archive/normal path routing through returned DF wrappers.
