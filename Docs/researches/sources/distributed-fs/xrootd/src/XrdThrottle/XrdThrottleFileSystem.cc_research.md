# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleFileSystem.cc

Purpose: implements SFS filesystem wrapper methods, forwarding metadata/control operations to the underlying filesystem and wrapping new files with throttle-aware `File` objects.

Important APIs/types/functions: `newDir()`, `newFile()`, `chksum()`, `chmod()`, `Connect()`, `Disc()`, `EnvInfo()`, `exists()`, `FAttr()`, `fsctl()`, `getChkPSize()`, `getStats()`, `getVersion()`, `gpFile()`, `mkdir()`, `prepare()`, `rem()`, `remdir()`, `rename()`, `stat()` overloads, and `truncate()`.

Control flow: every method except `newFile()` and `getVersion()` delegates directly to `m_sfs_ptr`. `newFile()` obtains a raw file from the underlying filesystem, wraps it in `unique_sfs_ptr`, constructs an `XrdThrottle::File`, and returns it. `getVersion()` reports `XrdVERSION`.

State and persistence: uses `m_sfs_ptr`, `m_throttle`, and `m_eroute` from the `FileSystem` instance; this file adds no state. Wrapped files own underlying file objects after construction.

Dependencies and integration: includes `XrdOfs/XrdOfs.hh` and `XrdThrottle.hh`. It is the pass-through layer that keeps the throttle plugin compatible with the full SFS interface.

Risks: null `m_sfs_ptr` would crash all pass-through methods, so configuration must complete before use. Only files are wrapped; directories and metadata operations are not throttled. Ownership transfer around pre-C++11 `auto_ptr` must be compiled carefully.

Test signals: wrap creation, null underlying `newFile()` handling, pass-through behavior for each SFS method, and version string reporting.
