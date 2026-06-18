<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.hh

Purpose: Declares `XrdPosixObject`, the common base and descriptor registry for POSIX-layer file and directory objects. It turns XRootD-backed `XrdPosixFile` and `XrdPosixDir` instances into POSIX-like integer file descriptors, tracks references, and provides locking and error-message storage.

Important APIs/types/functions: `AssignFD()` reserves a descriptor slot, optionally for a stream descriptor. `Init()` sizes the static descriptor table, `Shutdown()` tears it down, `Valid()` identifies descriptors owned by the XRootD POSIX layer, and `Release*()` removes file or directory objects from the registry. `File()` and `Dir()` map descriptors back to typed objects, with optional caller locking behavior. `Who()` is a virtual downcast hook implemented by derived file/dir classes. `ecMsg` stores object-specific extended error state.

Control flow and state: Static state includes `myFiles`, `baseFD`, `highFD`, `lastFD`, `freeFD`, `posxFD`, and `devNull`, protected by `fdMutex`. Per-object state includes `fdNum`, `refCnt`, a recursive update mutex, and an RW lock. The destructor automatically releases an assigned descriptor, so object lifetime is tied tightly to registry cleanup.

Dependencies/integration: Used throughout `XrdPosixXrootd.cc`, preload wrappers, and PSS to distinguish local descriptors from XRootD descriptors. It depends on XrdSys locking and atomics plus `XrdOucECMsg`.

Risks and test signals: Descriptor allocation/release bugs can surface as `EBADF`, descriptor leaks, accidental interception of local descriptors, or delayed-delete races. Tests should cover descriptor-table limits, concurrent `File()/ReleaseFile()`, close during outstanding async I/O, and object-specific `QueryError()` after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.hh -->
