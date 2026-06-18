# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottle.hh

Purpose: declares the OFS/SFS-facing throttle plugin classes that wrap an existing `XrdSfsFileSystem` and per-file `XrdSfsFile` objects.

Important APIs/types/functions: `XrdThrottle::File` overrides open, close, checkpoint, fctl, read/write variants, paged I/O, sync, stat, truncate, checksum info, and `SendData()`. `XrdThrottle::FileSystem` overrides SFS filesystem operations, mostly pass-through, plus static `Initialize()` and private `Configure()`. `unique_sfs_ptr` abstracts unique ownership for C++11 or pre-C++11 builds.

Control flow: `FileSystem::newFile()` wraps an underlying SFS file in `File`. `File::open()` identifies the user, prepares load-shed opaque data, increments open accounting, and delegates open. Data-transfer methods throttle then delegate. `FileSystem::Initialize()` constructs/configures the singleton plugin instance.

State and persistence: `File` stores open flag, wrapped file, hashed UID, load-shed opaque, connection ID, user, manager reference, and error route. `FileSystem` stores singleton state, logger/error route, trace object, config filename, underlying filesystem pointer, initialized flag, manager, and version info pointer.

Dependencies and integration: depends on `XrdSfsInterface.hh`, `XrdVersion.hh`, `XrdSysError`, `XrdThrottleTrace`, and `XrdThrottleManager`. It is exported through factory functions in `XrdThrottleFileSystemConfig.cc`.

Risks: many operations are pass-through and only file data-transfer paths are throttled. Sendfile and mmap are intentionally disabled because the plugin cannot observe bytes read through those paths. The singleton `FileSystem` initialization is documented as not thread-safe in the implementation.

Test signals: SFS factory load, wrapping of all file operations, data path throttling, pass-through metadata operations, disabled fd/mmap paths, singleton reuse, and version reporting.
