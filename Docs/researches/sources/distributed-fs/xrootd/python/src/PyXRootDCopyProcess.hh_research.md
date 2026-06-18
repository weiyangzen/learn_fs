# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.hh

## Purpose
This header defines the Python object type wrapping `XrdCl::CopyProcess`.

## Important APIs, Types, and Functions
`CopyProcess` exposes static methods `Parallel`, `AddJob`, `Prepare`, and `Run`. Its Python object stores `process`, `results`, and `parallel`. `CopyProcess_init` allocates the XrdCl process and result deque. `CopyProcess_dealloc` releases them. `CopyProcessMethods` and `CopyProcessType` define the Python-visible type.

## Control Flow
The initializer sets default parallelism to 1. Method dispatch is through Python C API method tables. Deallocation frees C++ resources when Python GC destroys the object.

## State and Persistence
In-memory state is the owned copy process, accumulated per-job results, and parallel setting. No direct persistence occurs in the header; copy operations are implemented in the source file.

## Dependencies and Integration Points
Depends on Python C API and XrdCl copy/property response headers. Included by module initialization and filesystem/copy implementation files.

## Risks and Test Signals
Because the type object is static in the header, include/ODR usage must remain controlled. Tests should verify construction/destruction does not leak, methods exist on the Python type, and repeated module import initializes the type safely.
