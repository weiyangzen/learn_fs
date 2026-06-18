# sources/distributed-fs/xrootd/python/src/PyXRootDFile.hh

## Purpose
This header declares the Python `File` binding type and its method surface.

## Important APIs, Types, and Functions
`class File` declares all static method implementations and stores `PyObject_HEAD`, `XrdCl::File *file`, and `uint64_t currentOffset`. It declares external `PyTypeObject FileType`.

## Control Flow
No method implementations are in the header; it defines the public C++ interface consumed by `ChunkIterator`, `PyXRootDFile.cc`, and module initialization.

## State and Persistence
The type's state is the owned XrdCl file handle and sequential-read offset. Persistence occurs only through operations implemented in the source file.

## Dependencies and Integration Points
Depends on Python C API, `Utils.hh`, XrdCl file types, and `deque`. It is the cross-file declaration needed by iterators, clone/template APIs, and module registration.

## Risks and Test Signals
The raw pointer ownership model requires correct deallocation and no use-after-free from iterators or clone references. Build tests catch signature drift; runtime tests should exercise object lifecycle and iterator interactions.
