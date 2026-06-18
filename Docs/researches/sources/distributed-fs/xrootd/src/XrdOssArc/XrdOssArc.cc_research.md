# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArc.cc

Purpose: implements the top-level archive OSS wrapper and plug-in entry point. It adds read-only archive/backup namespace behavior over an already loaded OSS.

Important APIs/types/functions: global `XrdOssArcGlobals`, extern "C" `XrdOssAddStorageSystem2`, `XrdOssArc::InitArc`, mutation blockers `Chmod/Create/Mkdir/Remdir/Rename/Truncate/Unlink`, `Features`, `FSctl`, `getErrMsg`, `Lfn2Pfn` overloads, and archive-aware `Stat`.

Control flow: `XrdOssAddStorageSystem2()` installs logging, constructs `XrdOssArc`, stores the underlying OSS pointer, initializes configuration, and returns the wrapper or null. `InitArc()` obtains a scheduler from env or starts a private one, logs startup, and delegates config. Mutation methods reject paths under archive/backup prefixes with `-EROFS`, otherwise pass through. `Lfn2Pfn` rejects internal archive paths with `-EPERM`. `Stat()` constructs `XrdOssArcCompose`; non-archive paths pass through, archive paths stat the archive zip on tape buffer, and file-in-archive requests ask backup utilities for metadata.

State and persistence behavior: installs global pointers (`ArcSS`, `ossP`, `schedP`), global config, logger, trace object, and thread-local extended error messages. It starts/schedules background backup work through configuration. It does not mutate archive contents through top-level namespace calls.

Dependencies: `XrdOssWrapper`, `XrdOssArcCompose`, `Config`, `Stage`, `ZipFile`, `XrdScheduler`, `XrdOucEnv`, `XrdOucECMsg`, `XrdSecEntity`, POSIX stat, and XRootD version macro.

Integration points: loaded as a pushed OSS plug-in by OFS, wrapping the native storage system. It advertises `XRDOSS_HASXERT` and creates archive-aware dir/file wrappers through the header.

Risks: global singleton design prevents independent instances; scheduler fallback creates an unmanaged scheduler; archive prefixes depend on configured strings; `getErrMsg()` returns only archive thread-local messages and not pass-through messages at top level; mutation checks must stay consistent with compose parsing.

Test signals: plug-in load/unload smoke, config failure returns null, mutation under `/archive` and `/backup` returns `EROFS`, normal paths pass through, stat archive zip vs member metadata, LFN mapping denial for internal paths, and feature flag preservation.
