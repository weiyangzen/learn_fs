## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixFile.hh

Purpose: declares `XrdPosixFile`, the central file object stored in the POSIX descriptor table and exposed as an `XrdOucCacheIO` backend.

Important APIs/types: inherits `XrdPosixObject`, `XrdOucCacheIO`, `XrdOucCacheIOCD`, and `XrdCl::ResponseHandler`. Public fields include `XCio`, `PrepIO`, `clFile`, stat metadata, delayed-destroy statics, structured-file suffix settings, and option flags `realFD`, `isStrm`, `isUpdt`. Methods cover offset management, close/finalize/stat, cache I/O operations, async response handling, location, and write size updates.

Control flow: descriptor lookups downcast via `Who(XrdPosixFile**)`. Cache operations call virtual `Read`, `Write`, `ReadV`, `Sync`, `Trunc`, `FSize`, `Fstat`, `Path`, `Location`, and page I/O methods. Offset and size are protected by `updMutex`, while object lifetime/descriptor access is protected by base-class locks and references.

State and persistence: maintains in-memory metadata and references for a single open remote file. Static delayed-destroy queues hold files that cannot be immediately closed/deleted.

Dependencies/integration: includes XrdCl file/filesystem/url/response types, `XrdOucCache`, `XrdPosixMap`, and `XrdPosixObject`. Used by standard wrappers, cache, extra page APIs, and response handlers.

Risks: public mutable metadata can be changed by collaborators. Header exposes implementation-specific statics. Correct lock ordering between object lock, update mutex, and FD mutex is critical. `FSize()` returns cached size under lock but may differ from remote if not refreshed.

Test signals: class-level tests with mocked `XrdCl::File`; offset update under concurrent reads/writes; cache detach lifecycle; destructor close accounting; static delayed-destroy configuration.
