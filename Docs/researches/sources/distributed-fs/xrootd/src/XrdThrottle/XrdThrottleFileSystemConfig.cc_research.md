# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystemConfig.cc

Purpose: provides the OFS/SFS plugin factory and initialization/configuration path for the throttle filesystem wrapper.

Important APIs/types/functions: local `LoadFS()`, `XrdThrottle::XrdSfsGetFileSystem_Internal()`, exported `XrdSfsGetFileSystem()` and `XrdSfsGetFileSystem2()`, `FileSystem::Initialize()`, constructor/destructor, and `FileSystem::Configure()`. Version symbols are declared with `XrdVERSIONINFO`.

Control flow: factory calls internal function; if the OSS throttle flag is set, it logs a compatibility warning and returns the native filesystem to avoid double stacking. Otherwise `Initialize()` creates/reuses the singleton, sets config/logging, calls `Configure()`, initializes the manager, and marks the instance initialized. `Configure()` parses throttle config, applies manager settings and trace mask, loads the underlying filesystem through `LoadFS()` or uses `native_fs`, exports `XRDOFSLIB`, attaches optional g-stream monitoring, and copies feature flags.

State and persistence: `FileSystem::m_instance` is a process-wide singleton. The loaded filesystem plugin handle is persisted via `XrdSysPlugin::Persist()`. Environment variable `XRDOFSLIB` is exported. Manager recompute thread starts during initialization.

Dependencies and integration: depends on `XrdSysPlugin`, `XrdSysLogger`, `XrdOucEnv`, `XrdOucStream`, `XrdThrottleConfig`, and the XrdSfs plugin ABI. It can load the default OFS directly or a custom `throttle.fslib`.

Risks: file notes that nothing is thread-safe; singleton initialization should happen during single-threaded startup. If `XrdOssThrottle` is loaded, current behavior is warning and bypass for backward compatibility but may become failure later. `LoadFS()` persists the dynamic library and assumes factory ABI compatibility. Reconfiguration after first initialization is ignored.

Test signals: plugin factory symbols, default OFS load, custom fslib load, native filesystem path, OSS-throttle bypass, failed config handling, feature propagation, and environment export.
